<div align="center">

# 🩺 Auskulta

**AI Machine Diagnosis Copilot — melihat, mendengarkan, dan mengingat kondisi mesin seperti dokter memeriksa pasien.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![COMPFEST](https://img.shields.io/badge/COMPFEST%2018-AI%20Innovation%20Challenge-e11d48)](https://compfest.id)

*Smart Manufacturing • AI for the Backbone of the Economy*

</div>

---

## 📖 Tentang Auskulta

> *"Auskultasi"* — teknik dokter memeriksa pasien: melihat gejala, mendengarkan tubuh, lalu menelusuri rekam medis sebelum memberi diagnosis.

Ketika mesin pabrik mulai menunjukkan gejala tidak normal, jawabannya sering kali **sudah pernah tercatat** — di laporan maintenance lama, SOP, atau ingatan teknisi senior — tapi terfragmentasi dan sulit ditelusuri. **Auskulta** adalah AI copilot yang menggabungkan tiga kemampuan sekaligus untuk memberi diagnosis kesehatan mesin yang cepat dan bisa dipertanggungjawabkan:

- 👁️ **Melihat** — deteksi anomali visual (getaran, gerakan tidak stabil) dari video mesin
- 👂 **Mendengarkan** — deteksi anomali dari suara mesin (sinyal tambahan, best-effort)
- 🧠 **Mengingat** — menelusuri histori maintenance untuk mencari kejadian serupa di masa lalu

Diagnosis akhir dihasilkan oleh LLM dan **selalu di-ground pada evidence historis nyata** — bukan tebakan bebas.

📄 Penjelasan lengkap (problem statement, novelty, business value, API spec) ada di [`docs/PROJECT_DETAIL.md`](docs/PROJECT_DETAIL.md).

## 📑 Daftar Isi

- [Fitur](#-fitur)
- [Arsitektur](#-arsitektur)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API](#-api)
- [Struktur Proyek](#-struktur-proyek)
- [Roadmap](#-roadmap)
- [Tim](#-tim)
- [Lisensi](#-lisensi)

## ✨ Fitur

- ✅ Deteksi anomali visual dari video (optical flow) — tanpa perlu dataset eksternal
- ✅ Deteksi anomali audio dari track suara video — sinyal tambahan, gagal dengan aman (graceful degradation)
- ✅ Organizational memory — retrieval histori maintenance berbasis semantic embedding (OpenAI), otomatis fallback ke TF-IDF kalau API tidak tersedia
- ✅ Diagnosis LLM yang di-ground pada evidence, lengkap dengan urgensi, estimasi downtime, dan rekomendasi tindakan
- ✅ Explainable reasoning trace ("Kenapa diagnosis ini?") — evidence visual, audio, dan historis ditampilkan terpisah dengan tingkat confidence
- ✅ Safety gate berbasis kode: sistem menolak memberi diagnosis spesifik kalau evidence historis tidak cukup mirip, alih-alih membiarkan LLM mengarang
- ✅ Fallback rule-based — sistem tetap memberi hasil meski LLM API tidak tersedia
- ✅ Satu alur interaksi sederhana: upload video → lihat laporan kesehatan mesin
- ✅ Deployment satu perintah lewat Docker Compose

## 🏗️ Arsitektur

```
Upload 1 video mesin
        │
        ▼
┌─────────────────┐     ┌─────────────────┐
│  Visual Anomaly  │     │  Audio Anomaly   │
│  (selalu jalan)   │     │  (best-effort)    │
└────────┬─────────┘     └────────┬─────────┘
         └───────────┬────────────┘
                      ▼
        ┌──────────────────────────┐
        │  Organizational Memory    │  Semantic embedding retrieval (fallback: TF-IDF)
        └─────────────┬────────────┘
                       ▼
        ┌──────────────────────────┐
        │  LLM Diagnosis             │  skor + evidence → satu diagnosis
        └─────────────┬────────────┘
                       ▼
         1 Laporan Kesehatan Mesin
```

Detail lengkap tiap komponen ada di [`docs/PROJECT_DETAIL.md`](docs/PROJECT_DETAIL.md#8-arsitektur-teknis).

## 🛠️ Tech Stack

| Layer | Teknologi |
|---|---|
| Backend | Python, FastAPI |
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Vision | OpenCV (optical flow) |
| Audio | librosa (fitur spektral) |
| Retrieval | OpenAI embeddings (semantic), fallback ke scikit-learn TF-IDF |
| Reasoning | LLM API (OpenAI-compatible) |
| Deployment | Docker Compose (backend), Next.js dev server (frontend) |

## 🚀 Quick Start

**Backend:**

```bash
git clone https://github.com/Ramane-Vision/auskulta.git
cd auskulta
cp .env.example .env
# isi LLM_API_KEY di .env

docker compose up --build
```

**Frontend (Next.js):**

```bash
cd frontend-next
cp .env.local.example .env.local
npm install
npm run dev
```

Buka [`http://localhost:3000`](http://localhost:3000), upload video mesin, klik **Analisis Video**.

_(Frontend vanilla JS lama di `frontend/` masih tersedia sebagai fallback, otomatis di-serve backend di `http://localhost:8000`.)_

## 🔌 API

`POST /api/analyze` — multipart form-data, field `file` (video: mp4/mov/avi/mkv/webm).

```json
{
  "visual": { "score": 0.62, "vibration_index": 0.41, "detected_events": [], "notes": "..." },
  "audio": { "score": 0.48, "spectral_flatness": 0.11, "zero_crossing_rate": 0.07, "notes": "..." },
  "risk_score": 0.57,
  "urgency": "tinggi",
  "diagnosis": "Kemungkinan bearing degradation, mirip dengan kasus MR-001...",
  "estimated_downtime_hours": 24,
  "recommended_action": "Jadwalkan inspeksi bearing dalam 24 jam ke depan.",
  "evidence": [
    { "id": "MR-001", "machine": "Conveyor Motor M-03", "symptom": "...", "root_cause": "...", "action_taken": "...", "downtime_hours": 6, "date": "2026-03-14", "similarity": 0.71 }
  ]
}
```

## 📂 Struktur Proyek

```
auskulta/
├── backend/
│   ├── main.py        # FastAPI app, endpoint POST /api/analyze
│   ├── vision.py       # deteksi anomali visual
│   ├── audio.py        # deteksi anomali audio (best-effort)
│   ├── knowledge.py    # organizational memory (embedding retrieval + TF-IDF fallback)
│   ├── diagnosis.py    # fusion + LLM diagnosis
│   └── config.py       # konfigurasi environment
├── frontend-next/       # UI utama (Next.js + TypeScript + Tailwind)
├── frontend/            # UI lama (vanilla JS), fallback yang masih di-serve backend
├── data/
│   └── knowledge_base.json   # histori maintenance
├── docs/
│   ├── PROJECT_DETAIL.md     # penjelasan lengkap proyek
│   └── PROPOSAL.md           # draft proposal submission
├── docker-compose.yml
└── Dockerfile
```

## 🗺️ Roadmap

MVP penyisihan ini sengaja dibatasi ke fondasi yang benar-benar bekerja. Peningkatan lebih lanjut direncanakan berlanjut di **Hackathon 10 jam babak final** (sesuai alur kompetisi AIC COMPFEST 18), bukan dikejar semua malam ini:

- [ ] Latih model audio anomaly detection di dataset publik MIMII secara penuh (bukan subset)
- [ ] Tambahkan pretrained visual event detector (asap, percikan)
- [ ] Perluas knowledge base dengan data maintenance riil dari mitra industri
- [ ] Ganti TF-IDF dengan embedding model semantik untuk retrieval yang lebih akurat
- [ ] Fitur Knowledge Gap Detection — deteksi gejala yang belum punya histori sama sekali
- [ ] Evaluation benchmark & kalibrasi threshold berbasis data berlabel

Detail lengkap: [`docs/PROJECT_DETAIL.md`](docs/PROJECT_DETAIL.md#12-roadmap-setelah-penyisihan-jika-lolos).

## 👥 Tim

| Nama | Peran |
|---|---|
| Achmad Naufal Fatkhi | Audio |
| Fawwaz Fathin Al Kautsar | RAG / LLM Backend |
| Muhammad Afif Aryaputra | Vision |
| Fery Nurjaman | Frontend / UI-UX |
| Maisya Talitha Salsa Bila | Official, Proposal, Video |

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

---

<div align="center">

Dibuat untuk **COMPFEST 18 — AI Innovation Challenge 2026**

</div>
