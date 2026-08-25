"""
Evaluation harness for Auskulta.

Runs the vision (+ audio, best-effort) pipeline against a set of labeled
test cases and reports precision/recall/F1/confusion matrix — turning
"trust us, it works" into an actual measured number for the proposal/demo.

Usage:
    python scripts/evaluate.py --cases eval_cases.json [--threshold 0.5]

`eval_cases.json` format:
[
  {"video": "/path/to/clip1.mp4", "expected_label": "normal"},
  {"video": "/path/to/clip2.mp4", "expected_label": "anomaly"},
  ...
]

`expected_label` must be "normal" or "anomaly" — a human ground-truth
label for what that clip actually shows. `risk_score >= threshold`
is treated as a predicted "anomaly", matching the diagnosis.py fusion
score before the LLM/evidence layer (this evaluates the *sensing*
layer's accuracy specifically, not the LLM's wording).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vision  # noqa: E402

try:
    import audio  # noqa: E402
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False


def combine_score(visual_score: float, audio_score: float | None) -> float:
    if audio_score is None:
        return visual_score
    return min((0.65 * visual_score) + (0.35 * audio_score), 1.0)


def evaluate(cases: list[dict], threshold: float) -> None:
    tp = fp = tn = fn = 0
    rows = []

    for case in cases:
        video_path = case["video"]
        expected = case["expected_label"]
        if expected not in ("normal", "anomaly"):
            print(f"  [skip] {video_path}: expected_label harus 'normal' atau 'anomaly', dapat '{expected}'")
            continue

        try:
            visual_result = vision.analyze_video(video_path)
        except Exception as exc:
            print(f"  [gagal] {video_path}: {exc}")
            continue

        audio_score = None
        if AUDIO_AVAILABLE:
            try:
                audio_result = audio.analyze_video(video_path)
                audio_score = audio_result.score
            except Exception:
                pass

        score = combine_score(visual_result.score, audio_score)
        predicted = "anomaly" if score >= threshold else "normal"
        correct = predicted == expected

        rows.append((Path(video_path).name, expected, predicted, round(score, 3), "OK" if correct else "SALAH"))

        if expected == "anomaly" and predicted == "anomaly":
            tp += 1
        elif expected == "normal" and predicted == "anomaly":
            fp += 1
        elif expected == "normal" and predicted == "normal":
            tn += 1
        elif expected == "anomaly" and predicted == "normal":
            fn += 1

    print(f"\n{'File':40s} {'Expected':10s} {'Predicted':10s} {'Score':8s} {'Result'}")
    print("-" * 85)
    for name, expected, predicted, score, result in rows:
        print(f"{name:40s} {expected:10s} {predicted:10s} {score:<8} {result}")

    total = tp + fp + tn + fn
    if total == 0:
        print("\nTidak ada kasus yang berhasil dievaluasi.")
        return

    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    print("\n=== CONFUSION MATRIX ===")
    print(f"                 Predicted Anomaly   Predicted Normal")
    print(f"Actual Anomaly   {tp:^18d} {fn:^18d}")
    print(f"Actual Normal    {fp:^18d} {tn:^18d}")

    print("\n=== METRICS ===")
    print(f"Accuracy : {accuracy:.2%}  ({tp + tn}/{total} benar)")
    print(f"Precision: {precision:.2%}")
    print(f"Recall   : {recall:.2%}")
    print(f"F1 Score : {f1:.2%}")
    print(f"\nCatatan: threshold={threshold}, n={total} kasus. Sample size kecil — laporkan angka ini")
    print("apa adanya di proposal (jangan dibulatkan jadi klaim akurasi besar tanpa konteks jumlah data).")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    with open(args.cases) as f:
        cases = json.load(f)

    evaluate(cases, args.threshold)


if __name__ == "__main__":
    main()
