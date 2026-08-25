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
- ✅ Organizational memory — retrieval histori maintenance berbasis kemiripan teks (TF-IDF)
- ✅ Diagnosis LLM yang di-ground pada evidence, lengkap dengan urgensi, estimasi downtime, dan rekomendasi tindakan
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
        │  Organizational Memory    │  TF-IDF retrieval atas histori maintenance
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
| Vision | OpenCV (optical flow) |
| Audio | librosa (fitur spektral) |
| Retrieval | scikit-learn (TF-IDF + cosine similarity) |
| Reasoning | LLM API (OpenAI-compatible) |
| Deployment | Docker Compose |

## 🚀 Quick Start

```bash
git clone https://github.com/Ramane-Vision/auskulta.git
cd auskulta
cp .env.example .env
# isi LLM_API_KEY di .env

docker compose up --build
```

Buka [`http://localhost:8000`](http://localhost:8000), upload video mesin, klik **Analisis Video**.

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
│   ├── knowledge.py    # organizational memory (TF-IDF retrieval)
│   ├── diagnosis.py    # fusion + LLM diagnosis
│   └── config.py       # konfigurasi environment
├── frontend/           # UI satu halaman
├── data/
│   └── knowledge_base.json   # histori maintenance
├── docs/
│   ├── PROJECT_DETAIL.md     # penjelasan lengkap proyek
│   └── PROPOSAL.md           # draft proposal submission
├── docker-compose.yml
└── Dockerfile
```

## 🗺️ Roadmap

- [ ] Latih model audio anomaly detection di dataset publik MIMII
- [ ] Tambahkan pretrained visual event detector (asap, percikan)
- [ ] Perluas knowledge base dengan data maintenance riil
- [ ] Ganti TF-IDF dengan embedding model semantik
- [ ] Fitur Knowledge Gap Detection

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
