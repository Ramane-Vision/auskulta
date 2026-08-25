export interface VisualScore {
  score: number;
  vibration_index: number;
  detected_events: string[];
  notes: string;
}

export interface AudioScore {
  score: number;
  spectral_flatness: number;
  zero_crossing_rate: number;
  notes: string;
}

export interface EvidenceItem {
  id: string;
  machine: string;
  symptom: string;
  root_cause: string;
  action_taken: string;
  downtime_hours: number;
  date: string;
  similarity: number;
}

export interface Reasoning {
  visual_evidence: string;
  audio_evidence: string;
  historical_evidence_summary: string;
  confidence: string;
}

export interface HealthReport {
  visual: VisualScore;
  audio: AudioScore | null;
  risk_score: number;
  urgency: "rendah" | "sedang" | "tinggi" | "kritis" | string;
  diagnosis: string;
  estimated_downtime_hours: number;
  recommended_action: string;
  evidence: EvidenceItem[];
  reasoning: Reasoning;
}
