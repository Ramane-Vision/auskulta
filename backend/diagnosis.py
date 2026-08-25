"""
LLM reasoning layer for Auskulta.

Takes the visual anomaly result (always present), an optional audio anomaly
result (best-effort — degrades gracefully if unavailable), and retrieved
evidence from organizational memory (past maintenance records), then turns
them into a human-readable diagnosis grounded in real historical incidents
instead of an LLM guessing freely.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional

from openai import OpenAI

import config
from knowledge import EvidenceRecord, retrieve_evidence
from vision import VisualAnomalyResult

try:
    from audio import AudioAnomalyResult
except ImportError:  # audio deps not installed in this environment
    AudioAnomalyResult = None  # type: ignore

SYSTEM_PROMPT = """Kamu adalah asisten diagnosa mesin industri untuk aplikasi bernama Auskulta.
Kamu menerima skor anomali visual (dan audio jika tersedia) dari sebuah mesin,
beserta catatan historis maintenance yang mirip (retrieved evidence), lalu
memberikan diagnosis singkat dalam Bahasa Indonesia yang bisa langsung dipakai
oleh teknisi pabrik.

Dasarkan jawabanmu SEUTUHNYA pada evidence historis yang diberikan. Jangan
mengarang penyebab yang tidak didukung oleh evidence. Jika evidence yang
diberikan kosong atau tidak relevan, katakan bahwa ini adalah kasus baru
yang belum ada di riwayat maintenance.

Selalu balas dalam format JSON dengan field berikut:
{
  "diagnosis": "penjelasan singkat kemungkinan penyebab anomali berdasarkan evidence, 1-3 kalimat",
  "urgency": "rendah" | "sedang" | "tinggi" | "kritis",
  "estimated_downtime_hours": angka perkiraan jam downtime jika tidak ditangani,
  "recommended_action": "tindakan konkret yang harus dilakukan teknisi",
  "cited_evidence_ids": ["daftar id evidence yang benar-benar dipakai sebagai dasar diagnosis"]
}

Jangan menambahkan teks lain di luar JSON tersebut."""


@dataclass
class Diagnosis:
    risk_score: float
    diagnosis: str
    urgency: str
    estimated_downtime_hours: float
    recommended_action: str
    evidence: List[EvidenceRecord] = field(default_factory=list)


def _build_query(visual: VisualAnomalyResult, audio: Optional["AudioAnomalyResult"]) -> str:
    parts = [visual.notes]
    if visual.detected_events:
        parts.append(" ".join(visual.detected_events))
    if audio is not None:
        parts.append(audio.notes)
    return " ".join(parts)


def _combine_score(visual: VisualAnomalyResult, audio: Optional["AudioAnomalyResult"]) -> float:
    if audio is None:
        return visual.score
    # Audio is treated as a best-effort secondary signal: it can raise the
    # combined score but is weighted less than vision, which is always
    # available and validated.
    return round(min((0.65 * visual.score) + (0.35 * audio.score), 1.0), 3)


def _fallback_diagnosis(
    visual: VisualAnomalyResult,
    audio: Optional["AudioAnomalyResult"],
    evidence: List[EvidenceRecord],
) -> Diagnosis:
    """Used if the LLM call fails (no API key, network issue, etc.) so the
    pipeline never breaks the demo end-to-end."""
    score = _combine_score(visual, audio)

    if score >= 0.75:
        urgency, hours, action = "kritis", 8.0, "Hentikan mesin segera dan lakukan inspeksi manual oleh teknisi senior."
    elif score >= 0.55:
        urgency, hours, action = "tinggi", 24.0, "Jadwalkan inspeksi dalam 24 jam ke depan sebelum kerusakan meluas."
    elif score >= 0.35:
        urgency, hours, action = "sedang", 72.0, "Pantau kondisi mesin lebih ketat pada shift berikutnya."
    else:
        urgency, hours, action = "rendah", 0.0, "Tidak ada tindakan segera diperlukan, kondisi mesin dalam batas normal."

    if evidence:
        top = evidence[0]
        diagnosis = (
            f"Diagnosis otomatis dari LLM tidak tersedia saat ini. Berdasarkan skor anomali "
            f"dan histori maintenance paling mirip ({top.id} - {top.machine}), kemungkinan penyebab "
            f"serupa dengan: {top.root_cause}."
        )
    else:
        diagnosis = "Diagnosis otomatis dari LLM tidak tersedia saat ini, dan tidak ditemukan histori maintenance yang mirip."

    return Diagnosis(
        risk_score=score,
        diagnosis=diagnosis,
        urgency=urgency,
        estimated_downtime_hours=hours,
        recommended_action=action,
        evidence=evidence,
    )


def generate_diagnosis(
    visual: VisualAnomalyResult, audio: Optional["AudioAnomalyResult"] = None
) -> Diagnosis:
    query = _build_query(visual, audio)
    evidence = retrieve_evidence(query, top_k=3)
    combined_score = _combine_score(visual, audio)

    if not config.LLM_API_KEY:
        return _fallback_diagnosis(visual, audio, evidence)

    try:
        client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        user_payload = {
            "visual_anomaly_score": visual.score,
            "visual_notes": visual.notes,
            "visual_detected_events": visual.detected_events,
            "audio_anomaly_score": audio.score if audio else None,
            "audio_notes": audio.notes if audio else "Sinyal audio tidak tersedia untuk video ini.",
            "combined_score": combined_score,
            "retrieved_evidence": [
                {
                    "id": e.id,
                    "machine": e.machine,
                    "symptom": e.symptom,
                    "root_cause": e.root_cause,
                    "action_taken": e.action_taken,
                    "downtime_hours": e.downtime_hours,
                    "date": e.date,
                    "similarity": e.similarity,
                }
                for e in evidence
            ],
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
            risk_score=combined_score,
            diagnosis=parsed["diagnosis"],
            urgency=parsed["urgency"],
            estimated_downtime_hours=float(parsed["estimated_downtime_hours"]),
            recommended_action=parsed["recommended_action"],
            evidence=evidence,
        )
    except Exception:
        return _fallback_diagnosis(visual, audio, evidence)
