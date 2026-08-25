"""
Audio anomaly analysis for Auskulta.

Baseline method (always available, no external dataset required):
  - Extract the audio track from the input video.
  - Compute spectral features (MFCC, spectral flatness, zero-crossing rate).
  - Combine their irregularity into a normalized anomaly score. Harsh,
    inconsistent, high-entropy sound tends to correlate with mechanical
    anomalies (grinding, knocking, uneven bearing wear, etc.).

Upgrade path (recommended if time allows):
  - Train a small anomaly-detection model (e.g. IsolationForest or a
    lightweight autoencoder on MFCCs) on the public MIMII dataset
    (Malfunctioning Industrial Machine Investigation and Inspection,
    Hitachi/DCASE). Save it to `models/audio_anomaly_model.joblib` and it
    will be picked up automatically here instead of the heuristic.
"""

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

import librosa
import numpy as np
from moviepy.editor import VideoFileClip

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
TRAINED_MODEL_PATH = MODELS_DIR / "audio_anomaly_model.joblib"


@dataclass
class AudioAnomalyResult:
    score: float  # 0.0 (normal) - 1.0 (severe anomaly)
    spectral_flatness: float
    zero_crossing_rate: float
    mfcc_variance: float
    notes: str = ""


def _extract_audio(video_path: str) -> str:
    clip = VideoFileClip(video_path)
    tmp = NamedTemporaryFile(suffix=".wav", delete=False)
    if clip.audio is None:
        clip.close()
        raise ValueError("Video tidak memiliki track audio.")
    clip.audio.write_audiofile(tmp.name, fps=16000, logger=None)
    clip.close()
    return tmp.name


def _heuristic_score(y: np.ndarray, sr: int) -> tuple[float, dict]:
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    flatness = librosa.feature.spectral_flatness(y=y)
    zcr = librosa.feature.zero_crossing_rate(y=y)

    mfcc_variance = float(np.mean(np.var(mfcc, axis=1)))
    flatness_mean = float(np.mean(flatness))
    zcr_mean = float(np.mean(zcr))

    # Heuristic fusion: noisier spectrum (high flatness), more erratic
    # zero-crossings, and higher MFCC variance all push the score up.
    # Coefficients were picked so a "clean" steady hum lands well under 0.5.
    raw = (0.5 * flatness_mean * 10) + (0.3 * zcr_mean * 15) + (0.2 * min(mfcc_variance / 400, 1.0))
    score = float(np.clip(raw, 0.0, 1.0))

    return score, {
        "mfcc_variance": mfcc_variance,
        "spectral_flatness": flatness_mean,
        "zero_crossing_rate": zcr_mean,
    }


def _trained_model_score(y: np.ndarray, sr: int) -> Optional[float]:
    if not TRAINED_MODEL_PATH.exists():
        return None
    try:
        import joblib

        model = joblib.load(TRAINED_MODEL_PATH)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        features = np.mean(mfcc, axis=1).reshape(1, -1)
        # IsolationForest: decision_function is higher for normal, lower/negative for anomalies.
        raw = -model.decision_function(features)[0]
        return float(np.clip((raw + 0.5), 0.0, 1.0))
    except Exception:
        return None


def analyze_video(video_path: str) -> AudioAnomalyResult:
    audio_path = _extract_audio(video_path)
    y, sr = librosa.load(audio_path, sr=16000, mono=True)

    trained_score = _trained_model_score(y, sr)
    heuristic_score, details = _heuristic_score(y, sr)

    if trained_score is not None:
        score = trained_score
        notes = "Skor dihitung menggunakan model anomaly detection terlatih (models/audio_anomaly_model.joblib)."
    else:
        score = heuristic_score
        notes = "Skor dihitung dari fitur spektral baseline (belum ada model terlatih di models/audio_anomaly_model.joblib)."

    return AudioAnomalyResult(
        score=round(score, 3),
        spectral_flatness=round(details["spectral_flatness"], 5),
        zero_crossing_rate=round(details["zero_crossing_rate"], 5),
        mfcc_variance=round(details["mfcc_variance"], 3),
        notes=notes,
    )
