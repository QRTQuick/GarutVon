from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header, Form
from typing import Any, Optional
import io
import base64
import gzip
from pathlib import Path
from PIL import Image
from garutvon.database import SessionLocal
from garutvon.database.models import ApiKey

app = FastAPI(title='GarutVON API', version='0.0.1')

ALLOWED_IMAGE_FORMATS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'tiff', 'ico'}
ALLOWED_TEXT_FORMATS = {'txt', 'text', 'md', 'markdown', 'html', 'csv', 'json', 'xml', 'yaml', 'yml', 'rtf'}


def _read_text_bytes(content: bytes, filename: str) -> str:
    try:
        return content.decode('utf-8', errors='ignore')
    except Exception:
        return ''


def _extract_api_key(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
) -> Optional[str]:
    if x_api_key:
        return x_api_key
    if authorization:
        auth = authorization.strip()
        if auth.lower().startswith('bearer '):
            return auth[7:].strip()
    return None


def _require_api_key(api_key: str = Depends(_extract_api_key)) -> ApiKey:
    if not api_key:
        raise HTTPException(status_code=401, detail='Missing API key')
    db = SessionLocal()
    try:
        key = db.query(ApiKey).filter_by(key=api_key, is_active=True).first()
        if not key:
            raise HTTPException(status_code=401, detail='Invalid API key')
        return key
    finally:
        db.close()


@app.get('/health')
def health():
    return {'status': 'healthy', 'service': 'GarutVON API'}


@app.get('/version')
def version():
    return {'latest_version': '1.0.0'}


@app.get('/supported-formats')
def supported_formats():
    return {
        'image_formats': sorted(list(ALLOWED_IMAGE_FORMATS)),
        'text_formats': sorted(list(ALLOWED_TEXT_FORMATS)),
    }


@app.get('/supported-image-formats')
def supported_image_formats():
    return {'image_formats': sorted(list(ALLOWED_IMAGE_FORMATS))}


@app.post('/extract-text', dependencies=[Depends(_require_api_key)])
async def extract_text(file: UploadFile = File(...)) -> Any:
    content = await file.read()
    text = _read_text_bytes(content, file.filename or 'upload')
    return {'filename': file.filename, 'bytes': len(content), 'text': text}


@app.post('/metadata', dependencies=[Depends(_require_api_key)])
async def metadata(file: UploadFile = File(...)) -> Any:
    content = await file.read()
    meta = {'filename': file.filename, 'bytes': len(content), 'content_type': file.content_type}
    try:
        img = Image.open(io.BytesIO(content))
        meta.update({'format': img.format, 'width': img.width, 'height': img.height, 'mode': img.mode})
    except Exception:
        pass
    return meta


@app.post('/compress', dependencies=[Depends(_require_api_key)])
async def compress(file: UploadFile = File(...)) -> Any:
    content = await file.read()
    compressed = gzip.compress(content)
    return {
        'filename': file.filename,
        'original_bytes': len(content),
        'compressed_bytes': len(compressed),
        'compressed_base64': base64.b64encode(compressed).decode('utf-8'),
    }


@app.post('/convert', dependencies=[Depends(_require_api_key)])
async def convert(target_format: str = Form(...), file: UploadFile = File(...)) -> Any:
    content = await file.read()
    target_format = target_format.lower().strip().lstrip('.')
    filename = file.filename or 'output'
    base_name = Path(filename).stem

    if target_format in ALLOWED_IMAGE_FORMATS:
        try:
            image = Image.open(io.BytesIO(content))
        except Exception:
            raise HTTPException(status_code=400, detail='Unable to read uploaded image')
        output_format = 'JPEG' if target_format in {'jpg', 'jpeg'} else target_format.upper()
        if output_format == 'ICO':
            image = image.convert('RGBA')
        output_buffer = io.BytesIO()
        try:
            image.save(output_buffer, format=output_format)
        except Exception:
            raise HTTPException(status_code=400, detail=f'Cannot convert image to {target_format}')
        output_bytes = output_buffer.getvalue()
        return {
            'filename': f'{base_name}.{target_format}',
            'target_format': target_format,
            'bytes': len(output_bytes),
            'converted_base64': base64.b64encode(output_bytes).decode('utf-8'),
        }

    if target_format in ALLOWED_TEXT_FORMATS:
        text = _read_text_bytes(content, filename)
        if text == '':
            raise HTTPException(status_code=400, detail='Unable to decode text content')
        output_bytes = text.encode('utf-8')
        return {
            'filename': f'{base_name}.{target_format if target_format != "text" else "txt"}',
            'target_format': target_format,
            'bytes': len(output_bytes),
            'converted_base64': base64.b64encode(output_bytes).decode('utf-8'),
            'text': text,
        }

    raise HTTPException(status_code=400, detail='Unsupported target format')


@app.post('/test-image-convert')
async def test_image_convert(target_format: str = Form(...), file: UploadFile = File(...)) -> Any:
    return await convert(target_format=target_format, file=file)


@app.post('/ocr', dependencies=[Depends(_require_api_key)])
async def ocr(file: UploadFile = File(...)) -> Any:
    content = await file.read()
    try:
        img = Image.open(io.BytesIO(content)).convert('RGB')
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(img)
            text = '\n'.join([r[1] for r in result])
            return {'filename': file.filename, 'text': text}
        except Exception:
            import pytesseract
            text = pytesseract.image_to_string(img)
            return {'filename': file.filename, 'text': text}
    except Exception:
        return {'filename': file.filename, 'text': ''}
