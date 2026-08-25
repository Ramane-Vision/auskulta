"""
Auskulta API — single endpoint that receives one video clip of a running
machine and returns one fused health report: visual anomaly detection
grounded in organizational memory (past maintenance records) via an LLM
diagnosis layer.

This intentionally keeps to a single input -> single output interaction,
per the AIC 2026 MVP scope rules: no auth, no history, no dashboards. The
organizational-memory knowledge base is preloaded at startup, not something
the user manages through the UI.
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


class EvidenceItem(BaseModel):
    id: str
    machine: str
    symptom: str
    root_cause: str
    action_taken: str
    downtime_hours: float
    date: str
    similarity: float


class HealthReport(BaseModel):
    visual: VisualScore
    risk_score: float
    urgency: str
    diagnosis: str
    estimated_downtime_hours: float
    recommended_action: str
    evidence: list[EvidenceItem]


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
        diagnosis = generate_diagnosis(visual_result)
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
        risk_score=diagnosis.risk_score,
        urgency=diagnosis.urgency,
        diagnosis=diagnosis.diagnosis,
        estimated_downtime_hours=diagnosis.estimated_downtime_hours,
        recommended_action=diagnosis.recommended_action,
        evidence=[
            EvidenceItem(
                id=e.id,
                machine=e.machine,
                symptom=e.symptom,
                root_cause=e.root_cause,
                action_taken=e.action_taken,
                downtime_hours=e.downtime_hours,
                date=e.date,
                similarity=e.similarity,
            )
            for e in diagnosis.evidence
        ],
    )
