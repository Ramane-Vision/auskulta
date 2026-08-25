const fileInput = document.getElementById("video-input");
const analyzeBtn = document.getElementById("analyze-btn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

const urgencyBadge = document.getElementById("urgency-badge");
const visualScoreEl = document.getElementById("visual-score");
const audioScoreEl = document.getElementById("audio-score");
const combinedScoreEl = document.getElementById("combined-score");
const diagnosisTextEl = document.getElementById("diagnosis-text");
const downtimeTextEl = document.getElementById("downtime-text");
const actionTextEl = document.getElementById("action-text");
const evidenceListEl = document.getElementById("evidence-list");
const rawJsonEl = document.getElementById("raw-json");

const URGENCY_LABEL = {
  rendah: "Normal",
  sedang: "Perlu Perhatian",
  tinggi: "Segera Tindak Lanjut",
  kritis: "Kritis",
};

analyzeBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    statusEl.textContent = "Pilih video terlebih dahulu.";
    return;
  }

  analyzeBtn.disabled = true;
  statusEl.textContent = "Menganalisis video (visual + evidence historis + diagnosis)...";
  resultEl.classList.add("hidden");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/analyze", { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Gagal menganalisis video.");
    }
    const data = await res.json();
    renderResult(data);
    statusEl.textContent = "Selesai.";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  } finally {
    analyzeBtn.disabled = false;
  }
});

function renderResult(data) {
  urgencyBadge.textContent = URGENCY_LABEL[data.urgency] || data.urgency;
  urgencyBadge.className = `urgency-badge urgency-${data.urgency}`;

  visualScoreEl.textContent = data.visual.score.toFixed(2);
  audioScoreEl.textContent = data.audio ? data.audio.score.toFixed(2) : "N/A";
  combinedScoreEl.textContent = data.risk_score.toFixed(2);

  diagnosisTextEl.textContent = data.diagnosis;
  downtimeTextEl.textContent =
    data.estimated_downtime_hours > 0
      ? `Estimasi ${data.estimated_downtime_hours} jam downtime jika tidak segera ditangani.`
      : "Tidak ada estimasi downtime signifikan saat ini.";
  actionTextEl.textContent = data.recommended_action;

  evidenceListEl.innerHTML = "";
  if (data.evidence.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Tidak ditemukan histori maintenance yang mirip — ini kemungkinan kasus baru.";
    evidenceListEl.appendChild(li);
  } else {
    data.evidence.forEach((e) => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${e.id} — ${e.machine}</strong> (${e.date}, kemiripan ${(e.similarity * 100).toFixed(0)}%)<br>
        Gejala: ${e.symptom}<br>
        Penyebab: ${e.root_cause}<br>
        Tindakan sebelumnya: ${e.action_taken} (downtime ${e.downtime_hours} jam)`;
      evidenceListEl.appendChild(li);
    });
  }

  rawJsonEl.textContent = JSON.stringify(data, null, 2);
  resultEl.classList.remove("hidden");
}
