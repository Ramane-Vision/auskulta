"""
LLM reasoning layer for Auskulta.

Takes the visual anomaly result (always present), an optional audio anomaly
result (best-effort — degrades gracefully if unavailable), and retrieved
evidence from organizational memory (past maintenance records), then turns
them into a human-readable diagnosis grounded in real historical incidents
instead of an LLM guessing freely.

Safety mechanism: how much the LLM is allowed to claim is gated by the
*evidence confidence tier*, computed in code (not just requested via
prompt). If no sufficiently similar historical case is found, the system
never lets the LLM assert a specific diagnosis — it explicitly reports
insufficient evidence instead. This is enforced deterministically, not
left to the LLM to decide on its own.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional

from openai import OpenAI

import config
from knowledge import EvidenceRecord, confidence_thresholds, retrieve_evidence
from vision import VisualAnomalyResult

try:
    from audio import AudioAnomalyResult
except ImportError:  # audio deps not installed in this environment
    AudioAnomalyResult = None  # type: ignore

# Evidence-confidence thresholds now come from knowledge.py's
# confidence_thresholds(method) since TF-IDF and embedding similarity live
# on different scales — see that module for the actual values.

SYSTEM_PROMPT = """Kamu adalah asisten diagnosa mesin industri untuk aplikasi bernama Auskulta.
Kamu HANYA dipanggil ketika sistem sudah memastikan ada evidence historis yang
cukup relevan (confidence sedang/tinggi) — jadi kamu boleh membuat diagnosis,
tapi TETAP wajib mendasarkannya seutuhnya pada evidence yang diberikan.
Jangan mengarang penyebab yang tidak didukung evidence, dan jangan mengklaim
kepastian lebih tinggi dari yang didukung data.

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
class Reasoning:
    visual_evidence: str
    audio_evidence: str
    historical_evidence_summary: str
    confidence: str  # "tinggi" | "sedang" | "tidak cukup evidence"


@dataclass
class Diagnosis:
    risk_score: float
    diagnosis: str
    urgency: str
    estimated_downtime_hours: float
    recommended_action: str
    evidence: List[EvidenceRecord] = field(default_factory=list)
    reasoning: Optional[Reasoning] = None


def _build_query(visual: VisualAnomalyResult, audio: Optional["AudioAnomalyResult"]) -> str:
    parts = [visual.notes]
    if visual.detected_events:
        parts.append(" ".join(visual.detected_events))
    if audio is not None:
        parts.append(audio.notes)
    return " ".join(parts)


def _combine_score(visual: VisualAnomalyResult, audio: Optional["AudioAnomalyResult"]) -> float:
    """Fuses the *physical* anomaly signals (how abnormal the machine looks
    and sounds right now). Historical similarity is deliberately NOT mixed
    into this number — a strong match to a past case should raise our
    confidence in the diagnosis, not the machine's physical risk score
    itself. Confidence is reported separately via `Reasoning.confidence`."""
    if audio is None:
        return visual.score
    return round(min((0.65 * visual.score) + (0.35 * audio.score), 1.0), 3)


def _evidence_confidence(evidence: List[EvidenceRecord]) -> str:
    if not evidence:
        return "tidak cukup evidence"
    strong, weak = confidence_thresholds(evidence[0].method)
    if evidence[0].similarity < weak:
        return "tidak cukup evidence"
    if evidence[0].similarity < strong:
        return "sedang"
    return "tinggi"


def _urgency_from_score(score: float) -> tuple[str, float, str]:
    if score >= 0.75:
        return "kritis", 8.0, "Hentikan mesin segera dan lakukan inspeksi manual oleh teknisi senior."
    if score >= 0.55:
        return "tinggi", 24.0, "Jadwalkan inspeksi dalam 24 jam ke depan sebelum kerusakan meluas."
    if score >= 0.35:
        return "sedang", 72.0, "Pantau kondisi mesin lebih ketat pada shift berikutnya."
    return "rendah", 0.0, "Tidak ada tindakan segera diperlukan, kondisi mesin dalam batas normal."


def _build_reasoning(
    visual: VisualAnomalyResult,
    audio: Optional["AudioAnomalyResult"],
    evidence: List[EvidenceRecord],
    confidence: str,
) -> Reasoning:
    audio_text = audio.notes if audio is not None else "Sinyal audio tidak tersedia untuk video ini."

    if not evidence:
        historical_summary = "Tidak ditemukan kasus historis yang cukup mirip di knowledge base."
    else:
        top = evidence[0]
        historical_summary = (
            f"Ditemukan {len(evidence)} kasus historis dengan pola serupa. "
            f"Kasus terdekat: {top.id} ({top.machine}, kemiripan {top.similarity * 100:.0f}%) — {top.root_cause}."
        )

    return Reasoning(
        visual_evidence=visual.notes,
        audio_evidence=audio_text,
        historical_evidence_summary=historical_summary,
        confidence=confidence,
    )


def _insufficient_evidence_diagnosis(
    visual: VisualAnomalyResult,
    audio: Optional["AudioAnomalyResult"],
    combined_score: float,
    reasoning: Reasoning,
) -> Diagnosis:
    """Deterministic safety gate: when there's no sufficiently similar past
    case, the system explicitly says so instead of letting an LLM invent a
    specific root cause. Urgency is still reported (it only needs the raw
    anomaly scores), but the diagnosis text is intentionally non-specific."""
    urgency, hours, _ = _urgency_from_score(combined_score)
    return Diagnosis(
        risk_score=combined_score,
        diagnosis=(
            "Anomali terdeteksi, tetapi belum ditemukan kasus historis yang cukup mirip di knowledge base "
            "untuk memberikan diagnosis penyebab spesifik. Ini kemungkinan kasus baru."
        ),
        urgency=urgency,
        estimated_downtime_hours=hours,
        recommended_action=(
            "Lakukan inspeksi manual oleh teknisi untuk mengidentifikasi penyebab, lalu catat hasilnya "
            "sebagai data baru di knowledge base agar kasus serupa berikutnya bisa terdeteksi otomatis."
        ),
        evidence=[],
        reasoning=reasoning,
    )


def _fallback_diagnosis(
    visual: VisualAnomalyResult,
    audio: Optional["AudioAnomalyResult"],
    evidence: List[EvidenceRecord],
    reasoning: Reasoning,
) -> Diagnosis:
    """Used if the LLM call fails (no API key, network issue, etc.) so the
    pipeline never breaks the demo end-to-end. Still evidence-grounded,
    just without LLM-generated prose."""
    score = _combine_score(visual, audio)
    urgency, hours, action = _urgency_from_score(score)

    top = evidence[0]
    diagnosis = (
        f"Diagnosis otomatis dari LLM tidak tersedia saat ini. Berdasarkan skor anomali "
        f"dan histori maintenance paling mirip ({top.id} - {top.machine}), kemungkinan penyebab "
        f"serupa dengan: {top.root_cause}."
    )

    return Diagnosis(
        risk_score=score,
        diagnosis=diagnosis,
        urgency=urgency,
        estimated_downtime_hours=hours,
        recommended_action=action,
        evidence=evidence,
        reasoning=reasoning,
    )


def generate_diagnosis(
    visual: VisualAnomalyResult, audio: Optional["AudioAnomalyResult"] = None
) -> Diagnosis:
    query = _build_query(visual, audio)
    evidence = retrieve_evidence(query, top_k=3)
    combined_score = _combine_score(visual, audio)
    confidence = _evidence_confidence(evidence)
    reasoning = _build_reasoning(visual, audio, evidence, confidence)

    # Hard safety gate: no sufficiently similar case -> never let an LLM
    # assert a specific root cause, regardless of prompt instructions.
    if confidence == "tidak cukup evidence":
        return _insufficient_evidence_diagnosis(visual, audio, combined_score, reasoning)

    if not config.LLM_API_KEY:
        return _fallback_diagnosis(visual, audio, evidence, reasoning)

    try:
        client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
        user_payload = {
            "visual_anomaly_score": visual.score,
            "visual_notes": visual.notes,
            "visual_detected_events": visual.detected_events,
            "audio_anomaly_score": audio.score if audio else None,
            "audio_notes": audio.notes if audio else "Sinyal audio tidak tersedia untuk video ini.",
            "combined_score": combined_score,
            "evidence_confidence": confidence,
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
            timeout=20,
        )
        parsed = json.loads(response.choices[0].message.content)

        return Diagnosis(
            risk_score=combined_score,
            diagnosis=parsed["diagnosis"],
            urgency=parsed["urgency"],
            estimated_downtime_hours=float(parsed["estimated_downtime_hours"]),
            recommended_action=parsed["recommended_action"],
            evidence=evidence,
            reasoning=reasoning,
        )
    except Exception:
        return _fallback_diagnosis(visual, audio, evidence, reasoning)
