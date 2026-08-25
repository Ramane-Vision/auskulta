"""
LLM reasoning layer for Auskulta.

Takes the structured outputs of the vision and audio anomaly modules and
turns them into a human-readable diagnosis: likely root cause, urgency,
estimated downtime cost, and recommended action. This is the layer that
turns two raw anomaly scores into an actual decision a technician can act on.
"""

import json
from dataclasses import dataclass

from openai import OpenAI

import config
from audio import AudioAnomalyResult
from vision import VisualAnomalyResult

SYSTEM_PROMPT = """Kamu adalah asisten diagnosa mesin industri untuk aplikasi bernama Auskulta.
Kamu menerima skor anomali visual dan audio dari sebuah mesin, lalu memberikan diagnosis
singkat dalam Bahasa Indonesia yang bisa langsung dipakai oleh teknisi pabrik.

Selalu balas dalam format JSON dengan field berikut:
{
  "diagnosis": "penjelasan singkat kemungkinan penyebab anomali, 1-3 kalimat",
  "urgency": "rendah" | "sedang" | "tinggi" | "kritis",
  "estimated_downtime_hours": angka perkiraan jam downtime jika tidak ditangani,
  "recommended_action": "tindakan konkret yang harus dilakukan teknisi"
}

Jangan menambahkan teks lain di luar JSON tersebut."""


@dataclass
class Diagnosis:
    combined_score: float
    diagnosis: str
    urgency: str
    estimated_downtime_hours: float
    recommended_action: str


def _combine_scores(visual: VisualAnomalyResult, audio: AudioAnomalyResult) -> float:
    # Weighted fusion: audio tends to be a slightly earlier/more sensitive
    # indicator for rotating machinery faults than visible vibration.
    return round((0.45 * visual.score) + (0.55 * audio.score), 3)


def _fallback_diagnosis(combined_score: float) -> Diagnosis:
    """Used if the LLM call fails (no API key, network issue, etc.) so the
    pipeline never breaks the demo end-to-end."""
    if combined_score >= 0.75:
        urgency, hours, action = "kritis", 8.0, "Hentikan mesin segera dan lakukan inspeksi manual oleh teknisi senior."
    elif combined_score >= 0.55:
        urgency, hours, action = "tinggi", 24.0, "Jadwalkan inspeksi dalam 24 jam ke depan sebelum kerusakan meluas."
    elif combined_score >= 0.35:
        urgency, hours, action = "sedang", 72.0, "Pantau kondisi mesin lebih ketat pada shift berikutnya."
    else:
        urgency, hours, action = "rendah", 0.0, "Tidak ada tindakan segera diperlukan, kondisi mesin dalam batas normal."

    return Diagnosis(
        combined_score=combined_score,
        diagnosis="Diagnosis otomatis dari LLM tidak tersedia saat ini, hasil berikut dihitung dari skor anomali gabungan sebagai fallback.",
        urgency=urgency,
        estimated_downtime_hours=hours,
        recommended_action=action,
    )


def generate_diagnosis(visual: VisualAnomalyResult, audio: AudioAnomalyResult) -> Diagnosis:
    combined_score = _combine_scores(visual, audio)

    if not config.LLM_API_KEY:
        return _fallback_diagnosis(combined_score)

    try:
        client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        user_payload = {
            "visual_anomaly_score": visual.score,
            "visual_notes": visual.notes,
            "visual_detected_events": visual.detected_events,
            "audio_anomaly_score": audio.score,
            "audio_notes": audio.notes,
            "combined_score": combined_score,
        }

        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        parsed = json.loads(response.choices[0].message.content)

        return Diagnosis(
            combined_score=combined_score,
            diagnosis=parsed["diagnosis"],
            urgency=parsed["urgency"],
            estimated_downtime_hours=float(parsed["estimated_downtime_hours"]),
            recommended_action=parsed["recommended_action"],
        )
    except Exception:
        return _fallback_diagnosis(combined_score)
