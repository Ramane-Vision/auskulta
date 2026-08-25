"""
Quick calibration helper for the audio HEURISTIC baseline (not the MIMII
model — that's parked). Run this directly against your own labeled test
clips to see whether normal vs. anomaly scores actually separate, without
going through Docker/the full API each time.

Usage:
    python scripts/calibrate_audio.py \\
        --normal-dir /path/to/normal_clips \\
        --anomaly-dir /path/to/anomaly_clips

Put whatever files you recorded (video or audio, any of the extensions
audio.py already supports) into two folders and point this at them.
"""

import argparse
import statistics
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import audio  # noqa: E402  (uses the real audio.py, same code path as the app)

EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wav", ".m4a"}


def score_folder(folder: Path) -> list[tuple[str, float]]:
    results = []
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() not in EXTENSIONS:
            continue
        try:
            result = audio.analyze_video(str(f))
            results.append((f.name, result.score))
        except Exception as exc:
            print(f"  [gagal] {f.name}: {exc}")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normal-dir", required=True, type=Path)
    parser.add_argument("--anomaly-dir", required=True, type=Path)
    args = parser.parse_args()

    print(f"Menganalisis clip NORMAL di {args.normal_dir} ...")
    normal_scores = score_folder(args.normal_dir)
    for name, score in normal_scores:
        print(f"  {name:40s} -> {score:.3f}")

    print(f"\nMenganalisis clip ANOMALI di {args.anomaly_dir} ...")
    anomaly_scores = score_folder(args.anomaly_dir)
    for name, score in anomaly_scores:
        print(f"  {name:40s} -> {score:.3f}")

    if not normal_scores or not anomaly_scores:
        print("\nTidak cukup data di salah satu folder. Tambahkan clip lalu coba lagi.")
        return

    n_vals = [s for _, s in normal_scores]
    a_vals = [s for _, s in anomaly_scores]

    print("\n=== RINGKASAN ===")
    print(f"Normal : mean={statistics.mean(n_vals):.3f}  min={min(n_vals):.3f}  max={max(n_vals):.3f}")
    print(f"Anomali: mean={statistics.mean(a_vals):.3f}  min={min(a_vals):.3f}  max={max(a_vals):.3f}")

    if max(n_vals) < min(a_vals):
        suggested = (max(n_vals) + min(a_vals)) / 2
        print(f"\n✅ Terpisah bersih. Threshold yang wajar: sekitar {suggested:.2f}")
        print("   (Threshold ini informatif saja — audio.py sendiri tidak pakai hard threshold,")
        print("    skornya langsung dipakai sebagai sinyal kontinu di diagnosis.py.)")
    elif statistics.mean(a_vals) > statistics.mean(n_vals):
        print("\n⚠️  Ada tumpang tindih, tapi rata-rata anomali masih lebih tinggi dari normal.")
        print("   Ini cukup untuk demo tapi tidak sempurna — masih bisa dipakai malam ini.")
    else:
        print("\n❌ Tidak ada pemisahan yang jelas — rata-rata anomali TIDAK lebih tinggi dari normal.")
        print("   Coba: rekam ulang clip anomali dengan perbedaan suara yang lebih jelas,")
        print("   atau sesuaikan bobot di audio.py -> _heuristic_score().")


if __name__ == "__main__":
    main()
