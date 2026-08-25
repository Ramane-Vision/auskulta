# Auskulta — Penjelasan Detail Proyek

Dokumen ini adalah versi lengkap/detail dari penjelasan proyek (problem statement, arsitektur, API, roadmap). Untuk README ringkas yang tampil di halaman utama GitHub, lihat [`README.md`](../README.md) di root repo.

COMPFEST 18 AI Innovation Challenge — Tema: *AI for the Backbone of the Economy* — Track: **Smart Manufacturing**

> "Auskultasi" — teknik dokter memeriksa pasien: melihat gejala, lalu menelusuri rekam medis sebelum memberi diagnosis. Auskulta melakukan hal yang sama untuk mesin pabrik.

## 1. Problem

Ketika sebuah mesin pabrik mulai menunjukkan gejala tidak normal (getaran, gerakan tersendat, dsb.), operator biasanya tidak tahu apakah itu tanda kerusakan serius atau sekadar variasi normal. Padahal jawabannya sering kali **sudah pernah tercatat** — di laporan maintenance lama, di SOP, atau di ingatan teknisi senior. Masalahnya, catatan-catatan itu **terfragmentasi**: tersebar di PDF, Excel, WhatsApp, dan kepala orang yang bisa saja resign kapan saja. Akibatnya, setiap gejala baru diperlakukan seperti kasus baru, padahal polanya sering berulang — dan keterlambatan diagnosis berarti downtime produksi yang mahal.

## 2. Target User

Operator dan teknisi maintenance di pabrik skala menengah yang punya histori data maintenance (laporan, SOP) tapi belum termanfaatkan sebagai basis pengambilan keputusan otomatis.

## 3. Solusi: Auskulta

Auskulta adalah AI copilot yang menggabungkan tiga kemampuan:

1. **Melihat** — mendeteksi anomali visual (getaran, gerakan tidak stabil) langsung dari video mesin yang sedang beroperasi. Sinyal utama, selalu dihitung, tidak butuh dataset eksternal.
2. **Mendengarkan** — menganalisis suara mesin dari audio track video yang sama untuk sinyal anomali tambahan. Sinyal sekunder best-effort: kalau gagal (mis. video tanpa audio, dependency tidak lengkap), sistem otomatis lanjut dengan sinyal visual saja tanpa gagal.
3. **Mengingat** — menelusuri histori maintenance mesin (organizational memory) untuk mencari kejadian serupa di masa lalu.

Hasilnya digabung oleh LLM menjadi satu diagnosis yang **di-ground pada evidence nyata** — bukan tebakan bebas — lengkap dengan tingkat urgensi, estimasi downtime, dan rekomendasi tindakan.

**Alur interaksi (1 input → 1 output, sesuai batasan MVP penyisihan AIC 2026):**

```
Upload 1 video mesin
        │
        ▼
┌────────────────────┐     ┌────────────────────┐
│  Visual Anomaly     │     │  Audio Anomaly      │
│  (optical flow,      │     │  (spektral, best-    │
│   selalu jalan)       │     │   effort, opsional)   │
└─────────┬───────────┘     └─────────┬───────────┘
          └───────────┬───────────────┘
                       ▼
          ┌────────────────────────┐
          │ Organizational Memory   │  Semantic embedding retrieval (utama)
          │ (RAG ringan)             │  + TF-IDF cosine similarity (fallback)
          └────────────┬────────────┘
                        ▼
          ┌────────────────────────┐
          │  LLM Diagnosis           │  gabungkan skor + evidence → satu diagnosis
          └────────────┬────────────┘
                        ▼
          1 Laporan Kesehatan Mesin
(skor visual, skor audio, skor risiko gabungan, urgensi, diagnosis, evidence, rekomendasi)
```

## 4. Kenapa AI, Bukan Sekadar Aturan If-Else?

- Deteksi anomali visual pakai computer vision (optical flow) — tidak bisa digantikan aturan statis karena pola gerakan mesin bervariasi per jenis mesin dan kondisi operasi.
- Pencarian histori maintenance yang mirip pakai semantic embedding retrieval (OpenAI) sebagai jalur utama — menangkap kemiripan makna, bukan sekadar kecocokan kata — dengan TF-IDF/cosine similarity sebagai fallback offline kalau API tidak tersedia.
- Sintesis diagnosis dari skor + banyak evidence historis ke dalam satu rekomendasi yang koheren adalah tugas reasoning yang pas untuk LLM, dengan instruksi ketat agar hanya menjawab berdasarkan evidence yang diberikan (mengurangi risiko halusinasi).

## 5. Apa yang Baru (Novelty)

Kebanyakan solusi predictive maintenance yang umum di kompetisi berhenti di `sensor → ML → prediksi rusak`, atau computer-vision defect detection generik. Auskulta berbeda karena:

- Menggabungkan **tiga modalitas AI** (vision + audio + retrieval-augmented reasoning) dalam satu pipeline, bukan satu model tunggal.
- Diagnosis **selalu bisa ditelusuri sumbernya** (evidence citation) — bukan kotak hitam. Ini penting untuk kepercayaan teknisi di lapangan.
- Tidak butuh sensor IoT atau kamera industri khusus — cukup video biasa (bahkan dari HP), jadi biaya adopsi rendah untuk pabrik skala menengah yang belum punya infrastruktur IoT.

## 6. MVP yang Didemokan

- Upload satu video mesin yang sedang beroperasi.
- Sistem menghitung skor anomali visual secara otomatis (tanpa perlu dataset eksternal — baseline optical flow selalu jalan).
- Sistem mencoba menghitung skor anomali audio dari track suara video yang sama (best-effort, tetap lanjut kalau gagal/tidak ada audio).
- Sistem mencari kejadian serupa dari knowledge base histori maintenance (saat ini beberapa record sintetis, dapat diperluas).
- LLM memberi satu diagnosis lengkap dengan evidence, urgensi, estimasi downtime, dan rekomendasi tindakan.
- Semua berjalan lewat satu halaman web sederhana, di-deploy dengan `docker compose up`.

## 7. Dampak & Business Value

- **Waktu diagnosis** yang tadinya butuh mencari-cari laporan lama atau menunggu teknisi senior, dipangkas jadi hitungan detik.
- **Knowledge retention** — pengetahuan dari teknisi senior yang sudah resign/pensiun tetap bisa diakses lewat histori maintenance yang terstruktur.
- **Pengurangan downtime** — deteksi dini dari pola visual + evidence historis memungkinkan tindakan preventif sebelum kerusakan meluas.
- **Target pembeli**: divisi maintenance pabrik manufaktur skala menengah (tekstil, F&B, elektronik) yang punya arsip laporan maintenance tapi belum memanfaatkannya secara digital.

## 8. Arsitektur Teknis

```
backend/
├── main.py        FastAPI app, 1 endpoint: POST /api/analyze
├── vision.py       deteksi anomali visual (OpenCV optical flow) — sinyal utama
├── audio.py        deteksi anomali audio (IsolationForest terlatih, fallback fitur spektral) — sinyal sekunder, best-effort
├── knowledge.py    organizational memory: embedding retrieval (utama) + TF-IDF (fallback)
├── diagnosis.py    fusion visual+audio+evidence → LLM diagnosis (dengan fallback rule-based)
└── config.py       konfigurasi env (LLM API key, dsb.)
frontend/
├── index.html      1 halaman: upload video → lihat laporan
├── app.js
└── style.css
data/
└── knowledge_base.json   histori maintenance sintetis
```

**Tech stack**: Python, FastAPI, OpenCV (vision), librosa + IsolationForest terlatih (audio), OpenAI embeddings + scikit-learn TF-IDF fallback (retrieval), LLM API (OpenAI-compatible, via `.env`), Docker Compose.

## 9. Menjalankan Secara Lokal

```bash
cp .env.example .env
# isi LLM_API_KEY di .env

docker compose up --build
```

Buka `http://localhost:8000`, upload video mesin, klik "Analisis Video".

## 10. API

`POST /api/analyze` — multipart form-data, field `file` (video: mp4/mov/avi/mkv/webm).

```json
{
  "visual": { "score": 0.62, "vibration_index": 0.41, "detected_events": [], "notes": "..." },
  "audio": { "score": 0.48, "spectral_flatness": 0.11, "zero_crossing_rate": 0.07, "notes": "..." },
  "risk_score": 0.57,
  "urgency": "tinggi",
  "diagnosis": "Kemungkinan bearing degradation, mirip dengan kasus MR-001 dan MR-007...",
  "estimated_downtime_hours": 24,
  "recommended_action": "Jadwalkan inspeksi bearing dalam 24 jam ke depan.",
  "evidence": [
    { "id": "MR-001", "machine": "Conveyor Motor M-03", "symptom": "...", "root_cause": "Bearing degradation...", "action_taken": "...", "downtime_hours": 6, "date": "2026-03-14", "similarity": 0.71 }
  ]
}
```

## 11. Yang Masih Perlu Disempurnakan (Known Limitations)

- Skor vision masih berbasis heuristik (optical flow) yang dikalibrasi manual, belum tervalidasi formal (precision/recall) terhadap dataset berlabel besar. Audio sudah pakai model terlatih (IsolationForest, DCASE 2023 Task 2) tapi juga belum ada evaluasi precision/recall formal.
- Optical flow dapat salah membaca goyangan kamera sebagai anomali mesin — rekaman sebaiknya menggunakan tripod/penyangga stabil.
- Jalur fallback retrieval (TF-IDF, aktif kalau embedding API tidak tersedia) berbasis kecocokan kata, bukan makna — sinonim/parafrasa antara gejala dan catatan histori mungkin tidak cocok di jalur ini.
- Deteksi visual api/asap masih heuristik warna (HSV), bukan model terlatih — bisa salah pada pencahayaan warna hangat yang tidak terkait anomali.
- Knowledge base masih berisi data sintetis, belum data maintenance riil dari pabrik.
- Belum ada automated test suite.

## 12. Roadmap Setelah Penyisihan (jika lolos)

- Perluas knowledge base dari data maintenance riil (bukan sintetis).
- Ganti heuristik warna api/asap dengan model deteksi objek visual terlatih (berlisensi jelas — MIT/Apache, bukan AGPL) atau dilatih sendiri oleh tim.
- Perluas data training audio (saat ini 500 sampel DCASE 2023 Task 2) dengan MIMII penuh atau data pabrik riil, dan tambahkan evaluasi precision/recall formal untuk model `models/audio_anomaly_model.joblib`.
- Tingkatkan jalur fallback retrieval (mis. embedding lokal ringan) supaya kualitas tidak terlalu turun saat API eksternal tidak tersedia.
- Tambahkan fitur "Knowledge Gap Detection" — menandai ketika sebuah gejala tidak punya histori sama sekali, sebagai sinyal SOP baru perlu dibuat.
- Tambahkan automated test suite dan evaluation benchmark berbasis dataset berlabel (harness sudah disiapkan di `backend/scripts/evaluate.py`).

## 13. Tim

_(isi nama tim & pembagian peran di sini)_
