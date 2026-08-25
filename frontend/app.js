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
  statusEl.textContent = "Menganalisis video (visual + audio + diagnosis)...";
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
  audioScoreEl.textContent = data.audio.score.toFixed(2);
  combinedScoreEl.textContent = data.combined_score.toFixed(2);

  diagnosisTextEl.textContent = data.diagnosis;
  downtimeTextEl.textContent =
    data.estimated_downtime_hours > 0
      ? `Estimasi ${data.estimated_downtime_hours} jam downtime jika tidak segera ditangani.`
      : "Tidak ada estimasi downtime signifikan saat ini.";
  actionTextEl.textContent = data.recommended_action;

  rawJsonEl.textContent = JSON.stringify(data, null, 2);
  resultEl.classList.remove("hidden");
}
