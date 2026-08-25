"use client";

import { useCallback, useRef, useState } from "react";
import type { HealthReport } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024; // matches backend limit
const ALLOWED_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"];

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

function Spinner() {
  return (
    <svg className="h-5 w-5 animate-spin text-white" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<HealthReport | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const pickFile = useCallback((f: File | null) => {
    setError(null);
    setResult(null);
    if (!f) {
      setFile(null);
      setPreviewUrl(null);
      return;
    }
    if (!ALLOWED_TYPES.includes(f.type) && !f.name.match(/\.(mp4|mov|avi|mkv|webm)$/i)) {
      setError("Format file tidak didukung. Gunakan mp4, mov, avi, mkv, atau webm.");
      return;
    }
    if (f.size > MAX_FILE_SIZE_BYTES) {
      setError(`Video terlalu besar (${formatBytes(f.size)}). Maksimum 100MB.`);
      return;
    }
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
  }, []);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragActive(false);
    const f = e.dataTransfer.files?.[0];
    if (f) pickFile(f);
  }

  function handleReset() {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

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
      setError(
        e instanceof Error
          ? e.message
          : "Tidak bisa terhubung ke server. Pastikan backend (docker compose) sedang berjalan."
      );
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
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${
              dragActive
                ? "border-blue-500 bg-blue-950/30"
                : "border-neutral-700 bg-neutral-950 hover:border-neutral-600"
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept="video/*"
              onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
              className="hidden"
            />
            {!file ? (
              <div>
                <p className="text-neutral-300">
                  Seret video mesin ke sini, atau <span className="text-blue-400 underline">klik untuk pilih file</span>
                </p>
                <p className="mt-1 text-xs text-neutral-500">mp4, mov, avi, mkv, webm — maksimum 100MB</p>
              </div>
            ) : (
              <div onClick={(e) => e.stopPropagation()}>
                {previewUrl && (
                  <video src={previewUrl} controls className="mx-auto mb-3 max-h-48 rounded-lg" />
                )}
                <p className="text-sm text-neutral-300">
                  {file.name} <span className="text-neutral-500">({formatBytes(file.size)})</span>
                </p>
                <button
                  onClick={handleReset}
                  className="mt-2 text-xs text-neutral-500 underline hover:text-neutral-300"
                >
                  Ganti video
                </button>
              </div>
            )}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading || !file}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-3 font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading && <Spinner />}
            {loading ? "Menganalisis video (visual + audio + evidence)..." : "Analisis Video"}
          </button>
          {error && (
            <p className="mt-3 rounded-lg bg-red-950 px-3 py-2 text-sm text-red-400">{error}</p>
          )}
        </section>

        {result && (
          <section className="mt-8 space-y-6">
            <div className="flex items-center justify-between">
              <span
                className={`inline-block rounded-full border px-3 py-1 text-sm font-semibold ${
                  URGENCY_STYLES[result.urgency] ?? URGENCY_STYLES.sedang
                }`}
              >
                {URGENCY_LABEL[result.urgency] ?? result.urgency}
              </span>
              <button
                onClick={handleReset}
                className="text-xs text-neutral-500 underline hover:text-neutral-300"
              >
                Analisis video lain
              </button>
            </div>

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
