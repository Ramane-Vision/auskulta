"""
Visual anomaly analysis for Auskulta.

Baseline method (always available, no external model/dataset required):
  - Sample frames from the input video.
  - Compute dense optical flow between consecutive frames as a proxy for
    mechanical vibration / irregular motion.
  - Turn the variance of flow magnitude into a normalized anomaly score.

Upgrade path (optional, if a pretrained detector is available):
  - Drop a pretrained smoke/spark/fire detection checkpoint (e.g. a YOLO
    model trained on a public Roboflow dataset) into `models/` and wire it
    up in `_detect_visual_events`. If no checkpoint is found, that signal
    is simply skipped and the optical-flow score is used on its own.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
YOLO_CHECKPOINT = MODELS_DIR / "visual_event_detector.pt"


@dataclass
class VisualAnomalyResult:
    score: float  # 0.0 (normal) - 1.0 (severe anomaly)
    vibration_index: float
    detected_events: list = field(default_factory=list)
    frames_analyzed: int = 0
    notes: str = ""


def _sample_frames(video_path: str, max_frames: int = 90):
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or max_frames
    step = max(1, frame_count // max_frames)

    idx = 0
    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 180))
            frames.append(gray)
        idx += 1

    cap.release()
    return frames


def _vibration_index(frames) -> float:
    if len(frames) < 2:
        return 0.0

    magnitudes = []
    for prev, curr in zip(frames[:-1], frames[1:]):
        flow = cv2.calcOpticalFlowFarneback(
            prev, curr, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        magnitudes.append(float(np.mean(mag)))

    magnitudes = np.array(magnitudes)
    # Irregular/jittery motion has high variance relative to its mean;
    # smooth steady-state operation has low variance.
    mean_mag = magnitudes.mean() + 1e-6
    variance_ratio = magnitudes.std() / mean_mag
    return float(variance_ratio)


def _detect_visual_events(video_path: str) -> list:
    """Optional pretrained-detector hook. No-op unless a checkpoint is present."""
    if not YOLO_CHECKPOINT.exists():
        return []

    try:
        from ultralytics import YOLO  # optional dependency, only needed if upgraded

        model = YOLO(str(YOLO_CHECKPOINT))
        results = model.predict(source=video_path, verbose=False)
        events = set()
        for r in results:
            for box in r.boxes:
                cls_name = model.names[int(box.cls)]
                events.add(cls_name)
        return sorted(events)
    except Exception:
        # If the optional model can't be loaded, degrade gracefully to the
        # baseline optical-flow signal instead of failing the whole request.
        return []


def analyze_video(video_path: str) -> VisualAnomalyResult:
    frames = _sample_frames(video_path)
    vibration_index = _vibration_index(frames)
    events = _detect_visual_events(video_path)

    # Normalize vibration_index (typically 0.0 - ~1.5 in practice) into 0-1.
    base_score = min(vibration_index / 1.2, 1.0)
    event_bonus = 0.25 if events else 0.0
    score = min(base_score + event_bonus, 1.0)

    notes = "Skor dihitung dari indeks getaran (optical flow)."
    if events:
        notes += f" Terdeteksi indikasi visual tambahan: {', '.join(events)}."
    if not YOLO_CHECKPOINT.exists():
        notes += " (Deteksi objek visual pretrained belum dipasang — hanya memakai baseline getaran.)"

    return VisualAnomalyResult(
        score=round(score, 3),
        vibration_index=round(vibration_index, 4),
        detected_events=events,
        frames_analyzed=len(frames),
        notes=notes,
    )
