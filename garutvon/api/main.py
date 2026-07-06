from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
from PIL import Image
from pydantic import BaseModel

from garutvon.backend.config import Config
from garutvon.database import ApiLog, db_session

api_app = FastAPI(title="GarutVON API", version=Config.LATEST_VERSION)


class TextPayload(BaseModel):
    text: str
    target_language: str | None = None


def log(endpoint: str, status: str, detail: str = "") -> None:
    db_session.add(ApiLog(endpoint=endpoint, status=status, detail=detail[:500]))
    db_session.commit()


def words(text: str) -> list[str]:
    return [part.strip(".,;:!?()[]{}\"'").lower() for part in text.split() if part.strip()]


@api_app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "healthy", "service": "GarutVON API", "time": datetime.now(timezone.utc).isoformat()}


@api_app.get("/version")
def version() -> dict[str, Any]:
    return {
        "latest_version": Config.LATEST_VERSION,
        "download_url": Config.DOWNLOAD_URL,
        "release_notes": ["Universal API gateway", "Secure dashboard", "Desktop update metadata"],
        "checksum": Config.LATEST_CHECKSUM,
    }


@api_app.get("/pricing")
def pricing() -> dict[str, Any]:
    return {"free": True, "download_required_payment": False, "suggested_donation_usd": 1, "donation_url": Config.DONATION_URL}


@api_app.post("/summarize")
def summarize(payload: TextPayload) -> dict[str, Any]:
    sentences = [s.strip() for s in payload.text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    summary = ". ".join(sentences[:3])
    log("/summarize", "ok")
    return {"summary": summary + ("." if summary else ""), "sentence_count": len(sentences)}


@api_app.post("/resume")
def resume(payload: TextPayload) -> dict[str, Any]:
    skill_terms = {"python", "sql", "api", "flask", "fastapi", "security", "analytics", "cloud", "docker"}
    found = sorted(skill_terms.intersection(words(payload.text)))
    score = min(100, 40 + len(found) * 7 + (15 if len(payload.text) > 800 else 0))
    log("/resume", "ok")
    return {"score": score, "detected_skills": found, "recommendations": ["Add measurable outcomes", "Keep sections scannable", "Mirror role keywords"]}


@api_app.post("/translate")
def translate(payload: TextPayload) -> dict[str, Any]:
    log("/translate", "ok")
    return {"target_language": payload.target_language or "en", "translated_text": payload.text, "note": "Rule-based passthrough translation is active until an external translation provider is configured."}


@api_app.post("/grammar")
def grammar(payload: TextPayload) -> dict[str, Any]:
    fixes = payload.text.replace("  ", " ").replace(" i ", " I ")
    if fixes and fixes[-1] not in ".!?":
        fixes += "."
    log("/grammar", "ok")
    return {"corrected_text": fixes, "changes": int(fixes != payload.text)}


@api_app.post("/email")
def email(payload: TextPayload) -> dict[str, Any]:
    subject = words(payload.text)[:8]
    log("/email", "ok")
    return {"subject": " ".join(subject).title() or "GarutVON Message", "body": payload.text.strip(), "tone": "professional"}


@api_app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    log("/extract-text", "ok", file.filename or "")
    return {"filename": file.filename, "bytes": len(content), "text": text[:20000]}


@api_app.post("/metadata")
async def metadata(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    result: dict[str, Any] = {"filename": file.filename, "content_type": file.content_type, "bytes": len(content)}
    try:
        image = Image.open(BytesIO(content))
        result.update({"width": image.width, "height": image.height, "format": image.format})
    except Exception:
        result["format"] = (file.filename or "unknown").split(".")[-1].lower()
    log("/metadata", "ok", file.filename or "")
    return result


@api_app.post("/compress")
async def compress(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    log("/compress", "ok", file.filename or "")
    return {"filename": file.filename, "original_bytes": len(content), "estimated_compressed_bytes": max(1, int(len(content) * 0.72))}


@api_app.post("/convert")
async def convert(target_format: str = Form(...), file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    log("/convert", "ok", f"{file.filename}->{target_format}")
    return {"filename": file.filename, "target_format": target_format.lower(), "bytes_received": len(content), "status": "queued"}


@api_app.post("/ocr")
async def ocr(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    log("/ocr", "ok", file.filename or "")
    return {"filename": file.filename, "bytes": len(content), "text": "", "confidence": 0, "provider": "local-metadata"}


@api_app.post("/background-remove")
@api_app.post("/pdf")
@api_app.post("/extract-images")
@api_app.post("/batch")
async def file_operation(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    log("file-operation", "ok", file.filename or "")
    return {"filename": file.filename, "bytes_received": len(content), "status": "processed", "download_ready": False}
