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
    """HSV color-heuristic cues for fire and smoke.

    Important calibration note (found via real test footage, not assumed):
    warm/saturated/bright industrial equipment colors (e.g. safety-yellow
    power tools) sit in the SAME hue range as fire in HSV space — hue alone
    cannot tell a yellow drill from an orange flame. Real fire flickers
    (its pixel coverage varies significantly frame-to-frame); a painted
    object's coverage stays roughly constant. So fire detection requires
    BOTH meaningful warm-color coverage AND high temporal variance in that
    coverage — not just a static color match.
    """
    if len(frames) < 4:
        return []

    fire_ratios = []
    smoke_ratios = []

    for frame in frames:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

        # Fire: warm hue (red-orange in OpenCV's 0-179 H range), high
        # saturation, high brightness. Hue capped tighter than a naive
        # "warm color" range to lean away from yellow industrial equipment.
        fire_mask = (h <= 15) & (s >= 130) & (v >= 160)
        fire_ratios.append(float(np.mean(fire_mask)))

        # Smoke proxy: desaturated, mid-to-bright regions.
        smoke_mask = (s <= 35) & (v >= 90) & (v <= 220)
        smoke_ratios.append(float(np.mean(smoke_mask)))

    events = []
    fire_mean = sum(fire_ratios) / len(fire_ratios)
    fire_std = (sum((r - fire_mean) ** 2 for r in fire_ratios) / len(fire_ratios)) ** 0.5
    fire_cv = fire_std / fire_mean if fire_mean > 1e-6 else 0.0
    # Require both real coverage (>3% of frame) and flicker (coefficient of
    # variation > 0.3) — a static colored object fails the flicker check.
    if fire_mean > 0.03 and fire_cv > 0.3:
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

    # Normalize vibration_index into 0-1. Divisor calibrated from real
    # handheld phone footage (2026-08-25): a static/idle object filmed
    # handheld already reads ~1.0-1.1 due to hand tremor alone, which
    # saturated this score at the old divisor (1.2) regardless of actual
    # machine state. Raised to 2.0 so handheld tremor noise doesn't
    # automatically max out the score — footage on a stable
    # tripod/mount (recommended for the actual demo) will read
    # considerably lower at rest, preserving good discrimination.
    base_score = min(vibration_index / 2.0, 1.0)
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
