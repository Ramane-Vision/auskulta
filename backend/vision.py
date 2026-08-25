"""
Visual anomaly analysis for Auskulta.

Two fully original, dependency-free signals — no external model, no
dataset, no third-party license to worry about:

  1. Vibration index: dense optical flow between consecutive frames as a
     proxy for mechanical vibration / irregular motion.
  2. Visual event cues: HSV color-heuristic detection of fire-like
     (warm, saturated, bright) and smoke-like (desaturated, spreading)
     regions in the frame.

Both are heuristic proxies, not trained classifiers — same philosophy as
the audio baseline in audio.py. They're deliberately conservative (biased
toward fewer false positives) since a wrongly-triggered "fire detected"
during a live demo is worse than a missed one.

Note on the YOLO hook that used to live here: we looked for a small
pretrained fire/smoke detection checkpoint to plug in, but the ones we
found were either AGPL-3.0 licensed (which would impose copyleft
obligations on the whole app if network-deployed) or had no license at
all (all-rights-reserved by default). Rather than use either without
proper compliance, we replaced it with the color-heuristic approach
below. A properly-licensed (MIT/Apache/BSD) or team-trained detector
remains a valid upgrade path for later — see `_detect_visual_events`.
"""

from dataclasses import dataclass, field
from typing import List

import cv2
import numpy as np


@dataclass
class VisualAnomalyResult:
    score: float  # 0.0 (normal) - 1.0 (severe anomaly)
    vibration_index: float
    detected_events: list = field(default_factory=list)
    frames_analyzed: int = 0
    notes: str = ""


def _sample_frames(video_path: str, max_frames: int = 90) -> List[np.ndarray]:
    """Returns resized BGR color frames (kept in color so the event-cue
    heuristic below can use hue/saturation; grayscale conversion for
    optical flow happens later, per-use)."""
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
            frames.append(cv2.resize(frame, (320, 180)))
        idx += 1

    cap.release()
    return frames


def _vibration_index(frames: List[np.ndarray]) -> float:
    if len(frames) < 2:
        return 0.0

    gray_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    magnitudes = []
    for prev, curr in zip(gray_frames[:-1], gray_frames[1:]):
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


def _detect_visual_events(frames: List[np.ndarray]) -> List[str]:
    """HSV color-heuristic cues for fire and smoke. Deliberately
    conservative thresholds to avoid false positives on ordinary gray
    machine bodies / concrete floors."""
    if len(frames) < 4:
        return []

    fire_hits = 0
    smoke_ratios = []

    for frame in frames:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

        # Fire: warm hue (red-orange-yellow in OpenCV's 0-179 H range),
        # high saturation, high brightness.
        fire_mask = (h <= 25) & (s >= 130) & (v >= 160)
        if float(np.mean(fire_mask)) > 0.02:  # >2% of frame
            fire_hits += 1

        # Smoke proxy: desaturated, mid-to-bright regions.
        smoke_mask = (s <= 35) & (v >= 90) & (v <= 220)
        smoke_ratios.append(float(np.mean(smoke_mask)))

    events = []
    if fire_hits / len(frames) > 0.3:
        events.append("indikasi_api")

    # Only flag smoke if haze coverage is trending UP over the clip (spreading),
    # not just statically present — a static gray machine body shouldn't trigger this.
    half = len(smoke_ratios) // 2
    if half > 0:
        first_half_avg = sum(smoke_ratios[:half]) / half
        second_half_avg = sum(smoke_ratios[half:]) / (len(smoke_ratios) - half)
        if second_half_avg > 0.4 and (second_half_avg - first_half_avg) > 0.15:
            events.append("indikasi_asap")

    return events


def analyze_video(video_path: str) -> VisualAnomalyResult:
    frames = _sample_frames(video_path)
    vibration_index = _vibration_index(frames)
    events = _detect_visual_events(frames)

    # Normalize vibration_index (typically 0.0 - ~1.5 in practice) into 0-1.
    base_score = min(vibration_index / 1.2, 1.0)
    event_bonus = 0.25 if events else 0.0
    score = min(base_score + event_bonus, 1.0)

    notes = "Skor dihitung dari indeks getaran (optical flow)."
    if events:
        notes += f" Terdeteksi indikasi visual tambahan (heuristik warna): {', '.join(events)}."

    return VisualAnomalyResult(
        score=round(score, 3),
        vibration_index=round(vibration_index, 4),
        detected_events=events,
        frames_analyzed=len(frames),
        notes=notes,
    )
