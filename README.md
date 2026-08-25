# Auskulta — AI Machine Health Monitor

COMPFEST 18 AIC — Smart Manufacturing | Tema: *AI for the Backbone of the Economy*

## Masalah

Teknisi senior sering bisa mendeteksi kerusakan mesin lebih awal hanya dari **suara** dan **pola gerak** mesin — pengalaman puluhan tahun yang tidak terdokumentasi. Ketika mereka resign atau pensiun, kemampuan diagnosis dini ini ikut hilang. Sementara itu, kerusakan mesin yang tidak terdeteksi lebih awal menyebabkan downtime produksi yang mahal — salah satu penyebab utama inefisiensi produksi di industri manufaktur Indonesia.

## Solusi

**Auskulta** ("auskultasi" — teknik dokter mendengarkan tubuh pasien dengan stetoskop) adalah AI yang meniru cara teknisi senior mendiagnosis mesin: **melihat** pola gerak/getaran dan **mendengarkan** suara mesin sekaligus, lalu memberikan satu diagnosis kesehatan mesin yang bisa langsung ditindaklanjuti.

**Alur interaksi (sesuai batasan MVP penyisihan):**

1. Input tunggal: satu video singkat mesin yang sedang beroperasi (video sudah mengandung frame visual + audio track).
2. Output tunggal: satu laporan kesehatan mesin — skor anomali visual, skor anomali audio, skor gabungan, tingkat urgensi, diagnosis, estimasi downtime, dan rekomendasi tindakan.

## Arsitektur AI (3 lapis)

```
video.mp4
   │
   ├── vision.py   → analisis optical flow (indeks getaran) + opsional deteksi objek visual pretrained
   │                  → visual_anomaly_score (0-1)
   │
   ├── audio.py    → ekstraksi audio track → fitur spektral (MFCC, spectral flatness, ZCR)
   │                  → audio_anomaly_score (0-1)
   │
   └── diagnosis.py → fusion kedua skor + LLM reasoning
                       → diagnosis, urgency, estimated downtime, recommended action
```

Baik `vision.py` maupun `audio.py` punya **baseline heuristik yang selalu berjalan tanpa dataset eksternal** (optical flow untuk visual, fitur spektral untuk audio), dengan **upgrade path** ke model terlatih:

- `models/visual_event_detector.pt` — pretrained/fine-tuned YOLO untuk deteksi kejadian visual spesifik (asap, percikan, dsb). Jika file ini ada, hasil deteksinya otomatis digabung ke skor visual.
- `models/audio_anomaly_model.joblib` — model anomaly detection (mis. IsolationForest) yang dilatih di atas dataset publik **MIMII** (Malfunctioning Industrial Machine Investigation and Inspection). Jika file ini ada, dipakai menggantikan heuristik baseline.

Ini memastikan sistem **selalu bisa didemokan end-to-end**, sekaligus terbuka untuk ditingkatkan akurasinya begitu model/dataset selesai disiapkan.

## Menjalankan Secara Lokal

```bash
cp .env.example .env
# isi LLM_API_KEY di .env

docker compose up --build
```

Buka `http://localhost:8000` di browser, upload video mesin, klik "Analisis Video".

## API

`POST /api/analyze` — multipart form-data dengan field `file` (video: mp4/mov/avi/mkv/webm).

Response:

```json
{
  "visual": { "score": 0.42, "vibration_index": 0.31, "detected_events": [], "notes": "..." },
  "audio": { "score": 0.61, "spectral_flatness": 0.12, "zero_crossing_rate": 0.08, "notes": "..." },
  "combined_score": 0.53,
  "urgency": "sedang",
  "diagnosis": "...",
  "estimated_downtime_hours": 24,
  "recommended_action": "..."
}
```

## Tech Stack

- Backend: Python, FastAPI
- Vision: OpenCV (optical flow), opsional YOLO (ultralytics)
- Audio: librosa (fitur spektral/MFCC), opsional IsolationForest terlatih di dataset MIMII
- Reasoning: LLM API (OpenAI-compatible endpoint, dikonfigurasi via `.env`)
- Deployment: Docker Compose

## Tim

_(isi nama tim & anggota di sini)_
