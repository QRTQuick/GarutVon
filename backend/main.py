import os
import hashlib
import time
import datetime
import uuid
from fastapi import FastAPI, Depends, Header, HTTPException, UploadFile, File, Form, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config import Config
from backend.services.converter import ImageConverterService
from database.models import SessionLocal, APIKey, APIUsage, ConversionHistory, User, Subscription

app = FastAPI(
    title="GarutVON Developer Cloud API",
    description="Automate universal file productivity and image conversions using ultra-fast cloud pipelines.",
    version="2.0.0"
)

# Enable CORS for cross-origin developer requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to fetch and validate developer API Key
async def verify_developer_key(
    request: Request,
    x_api_key: str = Header(None, alias="X-API-Key"),
    authorization: str = Header(None)
):
    api_key_raw = x_api_key
    if not api_key_raw and authorization and authorization.startswith("Bearer "):
        api_key_raw = authorization.split(" ")[1]
        
    if not api_key_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing. Provide a valid 'X-API-Key' header or Bearer token."
        )
        
    # Securely hash the input key to look it up in the database
    key_hash = hashlib.sha256(api_key_raw.encode()).hexdigest()
    
    db = SessionLocal()
    key_record = db.query(APIKey).filter_by(key_hash=key_hash, is_active=True).first()
    
    if not key_record:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked developer API Key."
        )
        
    # Verify account state
    user = db.query(User).filter_by(id=key_record.user_id, is_active=True).first()
    if not user:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Associated user account is currently disabled."
        )
        
    # Rate limit check based on Subscription Plan limits
    sub = db.query(Subscription).filter_by(user_id=user.id, status="active").first()
    limit = sub.plan.conversion_limit if sub else 10
    
    # Calculate usage
    one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    conversions_this_week = db.query(ConversionHistory).filter(
        ConversionHistory.user_id == user.id,
        ConversionHistory.created_at >= one_week_ago,
        ConversionHistory.status == "completed"
    ).count()
    
    if conversions_this_week >= limit:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Weekly programmatic allocation limit exceeded. Current plan limit is {limit} conversions/week."
        )
        
    # We pass key record and user database contexts forward
    ctx = {
        "user_id": user.id,
        "api_key_id": key_record.id,
        "key_record": key_record,
        "db": db
    }
    return ctx


# Helper middleware to log programmatic key API usages
def log_developer_usage(ctx, request: Request, status_code: int, response_time_ms: int):
    db = ctx["db"]
    try:
        usage = APIUsage(
            api_key_id=ctx["api_key_id"],
            endpoint=request.url.path,
            method=request.method,
            status_code=status_code,
            ip_address=request.client.host if request.client else "0.0.0.0",
            response_time_ms=response_time_ms,
            created_at=datetime.datetime.utcnow()
        )
        db.add(usage)
        
        # Update last used timestamp
        ctx["key_record"].last_used_at = datetime.datetime.utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to record api usage analytics: {e}")


# ==========================================
# WORKING SERVICE: DEVELOPER IMAGE CONVERT
# ==========================================

@app.post("/api/v1/convert/image")
async def developer_convert_image(
    request: Request,
    file: UploadFile = File(...),
    format: str = Form(...),
    ctx: dict = Depends(verify_developer_key)
):
    start_time = time.time()
    db = ctx["db"]
    target_format = format.strip().upper()
    
    if target_format not in ImageConverterService.SUPPORTED_OUTPUT_FORMATS:
        response_time = int((time.time() - start_time) * 1000)
        log_developer_usage(ctx, request, 400, response_time)
        db.close()
        raise HTTPException(status_code=400, detail=f"Unsupported target output format: {target_format}")
        
    # Read file content safely
    contents = await file.read()
    file_size = len(contents)
    
    ok, err_msg = ImageConverterService.validate_file(file.filename, file_size)
    if not ok:
        response_time = int((time.time() - start_time) * 1000)
        log_developer_usage(ctx, request, 400, response_time)
        db.close()
        raise HTTPException(status_code=400, detail=err_msg)
        
    # Save temporarily to disk for Pillow processing
    input_filename = f"dev_{uuid.uuid4().hex}_{file.filename}"
    input_path = os.path.join(Config.UPLOAD_FOLDER, input_filename)
    
    with open(input_path, "wb") as f:
        f.write(contents)
        
    # Perform header/MIME checks
    ok, err_msg = ImageConverterService.validate_image_header(input_path)
    if not ok:
        if os.path.exists(input_path):
            os.remove(input_path)
        response_time = int((time.time() - start_time) * 1000)
        log_developer_usage(ctx, request, 400, response_time)
        db.close()
        raise HTTPException(status_code=400, detail=err_msg)
        
    # Process conversion
    success, out_res, out_filename, output_size = ImageConverterService.convert_image(input_path, target_format)
    
    if os.path.exists(input_path):
        try:
            os.remove(input_path)
        except Exception:
            pass
            
    if not success:
        response_time = int((time.time() - start_time) * 1000)
        log_developer_usage(ctx, request, 500, response_time)
        db.close()
        raise HTTPException(status_code=500, detail=f"Conversion processing error: {out_res}")
        
    # Log conversion history context
    download_token = f"gv_dl_dev_{uuid.uuid4().hex}"
    try:
        input_format_ext = file.filename.split(".")[-1].upper() if "." in file.filename else "PNG"
        history = ConversionHistory(
            user_id=ctx["user_id"],
            api_key_id=ctx["api_key_id"],
            service_type="image_converter",
            input_file_name=file.filename,
            input_file_size=file_size,
            input_format=input_format_ext,
            output_format=target_format,
            status="completed",
            download_token=download_token,
            created_at=datetime.datetime.utcnow()
        )
        db.add(history)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging dev conversion: {e}")
        
    response_time = int((time.time() - start_time) * 1000)
    log_developer_usage(ctx, request, 200, response_time)
    db.close()
    
    # Return file download directly for API efficiency, matching Stripe or Linear experience!
    file_path = os.path.join(Config.OUTPUT_FOLDER, out_filename)
    return FileResponse(
        file_path,
        media_type=f"image/{target_format.lower()}",
        filename=f"converted_{file.filename.split('.')[0]}.{target_format.lower()}"
    )


# ==========================================
# DEVELOPER ANALYTICS ENDPOINTS
# ==========================================

@app.get("/api/v1/usage")
async def get_usage_dashboard(ctx: dict = Depends(verify_developer_key)):
    db = ctx["db"]
    usages = db.query(APIUsage).filter_by(api_key_id=ctx["api_key_id"]).order_by(APIUsage.created_at.desc()).limit(100).all()
    
    # Simple metrics grouping
    total_calls = len(usages)
    success_calls = sum(1 for u in usages if u.status_code == 200)
    failed_calls = total_calls - success_calls
    avg_latency = int(sum(u.response_time_ms for u in usages) / total_calls) if total_calls > 0 else 0
    
    logs = [{
        "endpoint": u.endpoint,
        "method": u.method,
        "status_code": u.status_code,
        "response_time_ms": u.response_time_ms,
        "date": u.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for u in usages]
    
    db.close()
    return {
        "status": "success",
        "analytics": {
            "total_calls_tracked": total_calls,
            "successful_requests": success_calls,
            "failed_requests": failed_calls,
            "average_latency_ms": avg_latency
        },
        "usage_logs": logs
    }


# ==========================================
# FUTURE SERVICES - "COMING SOON" programmatic responses
# ==========================================

@app.post("/api/v1/convert/pdf")
@app.post("/api/v1/convert/ocr")
@app.post("/api/v1/convert/document")
@app.post("/api/v1/convert/resume")
@app.post("/api/v1/convert/grammar")
@app.post("/api/v1/convert/translate")
@app.post("/api/v1/convert/ai-chat")
@app.post("/api/v1/convert/background-removal")
@app.post("/api/v1/convert/compress")
@app.post("/api/v1/convert/metadata")
@app.post("/api/v1/convert/video")
@app.post("/api/v1/convert/audio")
@app.post("/api/v1/convert/office")
@app.post("/api/v1/convert/zip")
async def developer_coming_soon():
    return JSONResponse(
        status_code=200,
        content={
            "status": "coming_soon",
            "message": "This service is currently under development."
        }
    )
