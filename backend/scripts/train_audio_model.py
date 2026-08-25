"""
Train the audio anomaly detection model used by Auskulta.

This trains an IsolationForest on MFCC features extracted EXACTLY the same
way as `audio.py`'s `_trained_model_score` expects (sr=16000, mono, n_mfcc=20,
mean over time), so the resulting model is a drop-in upgrade — once saved,
`audio.py` picks it up automatically with no other code changes.

Works with either:
  - A folder of MIMII-style .wav files (recommended: point --normal-dir at
    a `.../normal/` folder from the MIMII dataset, one machine type, one id)
  - A folder of your own recorded video/audio clips of "normal" operation

Usage:
    python scripts/train_audio_model.py \\
        --normal-dir /path/to/mimii/fan/id_00/normal \\
        --abnormal-dir /path/to/mimii/fan/id_00/abnormal \\
        --limit 200

`--abnormal-dir` is optional and only used to print a sanity-check report
(mean/std of the anomaly score for normal vs. abnormal clips) — it is NOT
used to fit the model. IsolationForest is a novelty-detection method: it
should only be trained on normal data.
"""

import argparse
import random
import sys
from pathlib import Path

import joblib
import librosa
import numpy as np
from sklearn.ensemble import IsolationForest

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".mp4", ".mov", ".m4a"}
MODEL_OUTPUT_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "audio_anomaly_model.joblib"


def list_audio_files(directory: Path, limit: int) -> list[Path]:
    files = [p for p in directory.rglob("*") if p.suffix.lower() in AUDIO_EXTENSIONS]
    if not files:
        raise ValueError(f"Tidak ada file audio/video ditemukan di {directory}")
    random.shuffle(files)
    return files[:limit]


def extract_features(path: Path) -> np.ndarray:
    """Mirrors audio.py's feature extraction exactly: sr=16000, mono,
    n_mfcc=20, mean over time axis -> 20-dim feature vector."""
    if path.suffix.lower() in {".mp4", ".mov", ".m4a"}:
        # video/container file: extract audio track first, same as audio.py
        from moviepy.editor import VideoFileClip
        from tempfile import NamedTemporaryFile

        clip = VideoFileClip(str(path))
        if clip.audio is None:
            clip.close()
            raise ValueError(f"{path} tidak punya audio track")
        tmp = NamedTemporaryFile(suffix=".wav", delete=False)
        clip.audio.write_audiofile(tmp.name, fps=16000, logger=None)
        clip.close()
        y, sr = librosa.load(tmp.name, sr=16000, mono=True)
    else:
        y, sr = librosa.load(str(path), sr=16000, mono=True)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    return np.mean(mfcc, axis=1)


def build_feature_matrix(files: list[Path]) -> np.ndarray:
    features = []
    for i, f in enumerate(files):
        try:
            features.append(extract_features(f))
            if (i + 1) % 20 == 0:
                print(f"  ...{i + 1}/{len(files)} file diproses")
        except Exception as exc:
            print(f"  [skip] {f.name}: {exc}")
    if not features:
        raise ValueError("Tidak ada file yang berhasil diekstrak fiturnya.")
    return np.vstack(features)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--normal-dir", required=True, type=Path, help="Folder berisi audio/video kondisi normal")
    parser.add_argument("--abnormal-dir", type=Path, default=None, help="(Opsional) folder kondisi anomali, untuk sanity check saja")
    parser.add_argument("--limit", type=int, default=200, help="Maksimum jumlah file dipakai per kelas (default 200)")
    parser.add_argument("--contamination", type=float, default=0.05, help="Estimasi proporsi outlier di data normal (default 0.05)")
    args = parser.parse_args()

    if not args.normal_dir.exists():
        print(f"ERROR: {args.normal_dir} tidak ditemukan.")
        sys.exit(1)

    print(f"Mengambil file dari {args.normal_dir} (maks {args.limit})...")
    normal_files = list_audio_files(args.normal_dir, args.limit)
    print(f"Ditemukan {len(normal_files)} file normal. Mengekstrak fitur MFCC...")
    X_normal = build_feature_matrix(normal_files)
    print(f"Feature matrix normal: {X_normal.shape}")

    print("Melatih IsolationForest...")
    model = IsolationForest(n_estimators=100, contamination=args.contamination, random_state=42)
    model.fit(X_normal)

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"Model tersimpan di {MODEL_OUTPUT_PATH}")

    # Sanity check on the training data itself
    normal_scores = -model.decision_function(X_normal)
    print(f"\nSkor anomali (mentah, sebelum normalisasi) pada data NORMAL:")
    print(f"  mean={normal_scores.mean():.3f}  std={normal_scores.std():.3f}  min={normal_scores.min():.3f}  max={normal_scores.max():.3f}")

    if args.abnormal_dir and args.abnormal_dir.exists():
        print(f"\nMengambil file dari {args.abnormal_dir} (maks {args.limit}) untuk sanity check...")
        abnormal_files = list_audio_files(args.abnormal_dir, args.limit)
        X_abnormal = build_feature_matrix(abnormal_files)
        abnormal_scores = -model.decision_function(X_abnormal)
        print(f"Skor anomali (mentah) pada data ABNORMAL:")
        print(f"  mean={abnormal_scores.mean():.3f}  std={abnormal_scores.std():.3f}  min={abnormal_scores.min():.3f}  max={abnormal_scores.max():.3f}")

        if abnormal_scores.mean() > normal_scores.mean():
            print("\n✅ OK: rata-rata skor abnormal LEBIH TINGGI dari normal — model berhasil membedakan.")
        else:
            print("\n⚠️  WARNING: rata-rata skor abnormal TIDAK lebih tinggi dari normal.")
            print("   Model ini mungkin belum cukup baik membedakan kondisi anomali.")
            print("   Coba: tambah jumlah data normal, atau turunkan --contamination, atau ganti machine type/id.")

    print("\nSelesai. audio.py akan otomatis memakai model ini di request berikutnya (tidak perlu restart kode lain).")


if __name__ == "__main__":
    main()
