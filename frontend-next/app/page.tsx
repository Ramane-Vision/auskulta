"use client";

import { useState } from "react";
import type { HealthReport } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const URGENCY_STYLES: Record<string, string> = {
  rendah: "bg-emerald-950 text-emerald-400 border-emerald-800",
  sedang: "bg-amber-950 text-amber-400 border-amber-800",
  tinggi: "bg-orange-950 text-orange-400 border-orange-800",
  kritis: "bg-red-950 text-red-400 border-red-800",
};

const URGENCY_LABEL: Record<string, string> = {
  rendah: "Normal",
  sedang: "Perlu Perhatian",
  tinggi: "Segera Tindak Lanjut",
  kritis: "Kritis",
};

const CONFIDENCE_STYLES: Record<string, string> = {
  tinggi: "bg-emerald-950 text-emerald-400",
  sedang: "bg-amber-950 text-amber-400",
  "tidak cukup evidence": "bg-neutral-800 text-neutral-400",
};

function ScoreBox({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div
      className={`flex-1 rounded-xl border p-4 text-center ${
        highlight ? "border-blue-600 bg-neutral-900" : "border-neutral-800 bg-neutral-900"
      }`}
    >
      <div className="text-xs text-neutral-400">{label}</div>
      <div className="mt-1 text-2xl font-bold text-neutral-100">{value}</div>
    </div>
  );
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<HealthReport | null>(null);

  async function handleAnalyze() {
    if (!file) {
      setError("Pilih video terlebih dahulu.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/api/analyze`, { method: "POST", body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Gagal menganalisis video.");
      }
      const data: HealthReport = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Terjadi kesalahan.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-950 px-4 py-12 text-neutral-100">
      <div className="mx-auto max-w-2xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">🩺 Auskulta</h1>
          <p className="mt-2 text-neutral-400">
            AI yang mendiagnosis kesehatan mesin seperti dokter — melihat &amp; mendengarkan gejala
            mesin, lalu menelusuri rekam medis mesin (histori maintenance) sebelum memberi diagnosis.
          </p>
        </header>

        <section className="rounded-2xl border border-neutral-800 bg-neutral-900 p-6">
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-neutral-300 file:mr-4 file:rounded-lg file:border-0 file:bg-neutral-800 file:px-4 file:py-2 file:text-sm file:text-neutral-100 hover:file:bg-neutral-700"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Menganalisis video..." : "Analisis Video"}
          </button>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </section>

        {result && (
          <section className="mt-8 space-y-6">
            <span
              className={`inline-block rounded-full border px-3 py-1 text-sm font-semibold ${
                URGENCY_STYLES[result.urgency] ?? URGENCY_STYLES.sedang
              }`}
            >
              {URGENCY_LABEL[result.urgency] ?? result.urgency}
            </span>

            <div className="flex gap-3">
              <ScoreBox label="Skor Visual" value={result.visual.score.toFixed(2)} />
              <ScoreBox label="Skor Audio" value={result.audio ? result.audio.score.toFixed(2) : "N/A"} />
              <ScoreBox label="Skor Risiko" value={result.risk_score.toFixed(2)} highlight />
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-sm font-semibold text-neutral-400">Diagnosis</h2>
              <p className="mt-1 text-neutral-100">{result.diagnosis}</p>
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-sm font-semibold text-neutral-400">Estimasi Downtime</h2>
              <p className="mt-1 text-neutral-100">
                {result.estimated_downtime_hours > 0
                  ? `Estimasi ${result.estimated_downtime_hours} jam downtime jika tidak segera ditangani.`
                  : "Tidak ada estimasi downtime signifikan saat ini."}
              </p>
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="text-sm font-semibold text-neutral-400">Rekomendasi Tindakan</h2>
              <p className="mt-1 text-neutral-100">{result.recommended_action}</p>
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-neutral-400">
                Kenapa diagnosis ini?
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    CONFIDENCE_STYLES[result.reasoning.confidence] ?? CONFIDENCE_STYLES["tidak cukup evidence"]
                  }`}
                >
                  {result.reasoning.confidence}
                </span>
              </h2>
              <ul className="mt-3 space-y-2 text-sm text-neutral-300">
                <li>
                  <span className="font-medium text-neutral-100">Evidence visual:</span>{" "}
                  {result.reasoning.visual_evidence}
                </li>
                <li>
                  <span className="font-medium text-neutral-100">Evidence audio:</span>{" "}
                  {result.reasoning.audio_evidence}
                </li>
                <li>
                  <span className="font-medium text-neutral-100">Evidence historis:</span>{" "}
                  {result.reasoning.historical_evidence_summary}
                </li>
              </ul>
            </div>

            <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
              <h2 className="mb-3 text-sm font-semibold text-neutral-400">
                Evidence dari Histori Maintenance
              </h2>
              {result.evidence.length === 0 ? (
                <p className="text-sm text-neutral-400">
                  Tidak ditemukan histori maintenance yang mirip — ini kemungkinan kasus baru.
                </p>
              ) : (
                <ul className="space-y-3">
                  {result.evidence.map((e) => (
                    <li key={e.id} className="rounded-lg border border-neutral-800 bg-neutral-950 p-3 text-sm">
                      <div className="font-semibold text-neutral-100">
                        {e.id} — {e.machine}{" "}
                        <span className="font-normal text-neutral-500">
                          ({e.date}, kemiripan {(e.similarity * 100).toFixed(0)}%)
                        </span>
                      </div>
                      <div className="mt-1 text-neutral-300">Gejala: {e.symptom}</div>
                      <div className="text-neutral-300">Penyebab: {e.root_cause}</div>
                      <div className="text-neutral-300">
                        Tindakan sebelumnya: {e.action_taken} (downtime {e.downtime_hours} jam)
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <details className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5 text-sm text-neutral-400">
              <summary className="cursor-pointer font-medium text-neutral-300">
                Detail teknis (untuk teknisi)
              </summary>
              <pre className="mt-3 overflow-x-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
            </details>
          </section>
        )}
      </div>
    </main>
  );
}
