from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from ..db import get_db
from ..schemas import SummarizeIn, SummarizeOut
from ..auth import get_api_key
from ..models import ApiLog
from ..services import summarize, extract_text, metadata, convert, compress, background_remove

router = APIRouter(prefix="", tags=["core"])


async def log(db: AsyncSession, endpoint: str, status: str, detail: str = "") -> None:
    db.add(ApiLog(endpoint=endpoint, status=status, detail=(detail or "")[:500]))
    await db.commit()


@router.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "healthy", "service": "GarutVON API"}


@router.get("/version")
async def version() -> dict[str, Any]:
    return {
        "latest_version": "0.0.1",
        "download_url": None,
        "release_notes": [],
        "checksum": None,
    }


@router.post("/summarize", response_model=SummarizeOut)
async def summarize_text(
    payload: SummarizeIn,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
) -> SummarizeOut:
    result = summarize(payload.text)
    await log(db, "/summarize", "ok")
    return SummarizeOut(summary=result["summary"], sentence_count=result["sentence_count"])


@router.post("/extract-text")
async def extract_text_endpoint(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
):
    content = await file.read()
    result = extract_text(content, file.filename or "upload.txt", file.content_type)
    await log(db, "/extract-text", "ok", file.filename or "")
    return result


@router.post("/metadata")
async def metadata_endpoint(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
):
    content = await file.read()
    result = metadata(content, file.filename or "upload.bin", file.content_type)
    await log(db, "/metadata", "ok", file.filename or "")
    return result


@router.post("/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
):
    content = await file.read()
    result = extract_text(content, file.filename or "upload.png", file.content_type)
    await log(db, "/ocr", "ok", file.filename or "")
    return {"filename": file.filename, "text": result.get("text", ""), "bytes": result.get("bytes", 0)}


@router.post("/convert")
async def convert_endpoint(
    target_format: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
):
    content = await file.read()
    result = convert(content, file.filename or "upload.bin", target_format, file.content_type)
    await log(db, "/convert", "ok", file.filename or "")
    return result


@router.post("/compress")
async def compress_endpoint(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
):
    content = await file.read()
    result = compress(content, file.filename or "upload.bin", file.content_type)
    await log(db, "/compress", "ok", file.filename or "")
    return result


@router.post("/background-remove")
async def background_remove_endpoint(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_api_key),
):
    content = await file.read()
    result = background_remove(content, file.filename or "upload.png", file.content_type)
    await log(db, "/background-remove", "ok", file.filename or "")
    return result
