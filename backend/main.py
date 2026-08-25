"""
Auskulta API — single endpoint that receives one video clip of a running
machine and returns one fused health report (visual + audio + LLM diagnosis).

This intentionally keeps to a single input -> single output interaction,
per the AIC 2026 MVP scope rules: no auth, no history, no dashboards.
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import audio
import vision
from diagnosis import generate_diagnosis

app = FastAPI(title="Auskulta API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


class VisualScore(BaseModel):
    score: float
    vibration_index: float
    detected_events: list[str]
    notes: str


class AudioScore(BaseModel):
    score: float
    spectral_flatness: float
    zero_crossing_rate: float
    notes: str


class HealthReport(BaseModel):
    visual: VisualScore
    audio: AudioScore
    combined_score: float
    urgency: str
    diagnosis: str
    estimated_downtime_hours: float
    recommended_action: str


@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.post("/api/analyze", response_model=HealthReport)
async def analyze(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format file tidak didukung: {suffix}")

    with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        visual_result = vision.analyze_video(tmp_path)
        audio_result = audio.analyze_video(tmp_path)
        diagnosis = generate_diagnosis(visual_result, audio_result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gagal memproses video: {exc}") from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return HealthReport(
        visual=VisualScore(
            score=visual_result.score,
            vibration_index=visual_result.vibration_index,
            detected_events=visual_result.detected_events,
            notes=visual_result.notes,
        ),
        audio=AudioScore(
            score=audio_result.score,
            spectral_flatness=audio_result.spectral_flatness,
            zero_crossing_rate=audio_result.zero_crossing_rate,
            notes=audio_result.notes,
        ),
        combined_score=diagnosis.combined_score,
        urgency=diagnosis.urgency,
        diagnosis=diagnosis.diagnosis,
        estimated_downtime_hours=diagnosis.estimated_downtime_hours,
        recommended_action=diagnosis.recommended_action,
    )
