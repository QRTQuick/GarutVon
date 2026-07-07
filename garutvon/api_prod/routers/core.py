from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from ..db import get_db
from ..schemas import SummarizeIn, SummarizeOut
from ..auth import get_api_key, get_current_user
from ..models import ApiLog

router = APIRouter(prefix="/api", tags=["core"])


async def log(db: AsyncSession, endpoint: str, status: str, detail: str = "") -> None:
    db.add(ApiLog(endpoint=endpoint, status=status, detail=(detail or "")[:500]))
    await db.commit()


@router.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "healthy", "service": "GarutVON API"}


@router.get("/version")
async def version() -> dict[str, Any]:
    return {"latest_version": "0.0.1", "download_url": None, "release_notes": [], "checksum": None}


@router.post("/summarize", response_model=SummarizeOut)
async def summarize(payload: SummarizeIn, db: AsyncSession = Depends(get_db), api_key=Depends(get_api_key)) -> SummarizeOut:
    # simple, deterministic summarizer for now
    sentences = [s.strip() for s in payload.text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    summary = ". ".join(sentences[:3])
    await log(db, "/summarize", "ok")
    return SummarizeOut(summary=(summary + ("." if summary else "")), sentence_count=len(sentences))


@router.post("/extract-text")
async def extract_text(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), api_key=Depends(get_api_key)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")[:20000]
    await log(db, "/extract-text", "ok", file.filename or "")
    return {"filename": file.filename, "bytes": len(content), "text": text}


@router.post("/metadata")
async def metadata(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), api_key=Depends(get_api_key)):
    content = await file.read()
    await log(db, "/metadata", "ok", file.filename or "")
    # minimal metadata: size and filename
    return {"filename": file.filename, "bytes": len(content), "content_type": file.content_type}


@router.post("/ocr")
async def ocr(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), api_key=Depends(get_api_key)):
    # placeholder that logs the request; pluggable to real OCR engines
    _ = await file.read()
    await log(db, "/ocr", "ok", file.filename or "")
    return {"filename": file.filename, "text": "", "confidence": 0}


@router.post("/convert")
async def convert(target_format: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), api_key=Depends(get_api_key)):
    _ = await file.read()
    await log(db, "/convert", "queued", f"to={target_format}")
    return {"filename": file.filename, "target_format": target_format, "status": "queued"}
