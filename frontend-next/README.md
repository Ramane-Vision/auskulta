# Auskulta Frontend (Next.js)

Frontend baru berbasis Next.js + TypeScript + Tailwind CSS, menggantikan frontend vanilla JS di `../frontend/` (masih ada, dipertahankan sebagai fallback — backend tetap bisa serve versi lama itu langsung tanpa Next.js kalau dibutuhkan).

## Menjalankan secara lokal

Backend (FastAPI) harus sudah jalan lebih dulu di `http://localhost:8000` (lihat README utama di root repo — `docker compose up --build` dari root project).

```bash
cd frontend-next
cp .env.local.example .env.local
npm install
npm run dev
```

Buka `http://localhost:3000`.

## Catatan

- Backend sudah CORS permissive (`allow_origins=["*"]`), jadi frontend ini bisa langsung fetch ke backend tanpa konfigurasi tambahan apa pun di sisi backend.
- `NEXT_PUBLIC_API_URL` di `.env.local` menentukan alamat backend yang dipanggil — ubah kalau backend jalan di alamat/port lain.
- Belum digabung ke `docker-compose.yml` di root (sengaja, untuk menjaga scope malam penyisihan tetap kecil) — bisa ditambahkan sebagai service terpisah di tahap final kalau diperlukan.
