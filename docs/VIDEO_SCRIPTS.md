# Naskah Video — Auskulta

Isi `[ISI: ...]` sebelum syuting. Baca naskah ini sebagai panduan, boleh disesuaikan gaya bicara asal isinya tetap sama.

---

# 1. PROOF OF WORK VIDEO (≤7 menit, YouTube unlisted)

Format nama file: `COMPFEST 18 AIC: PROOF OF WORK - [Nama Tim] - Auskulta`

Tujuan video ini BUKAN meyakinkan orang bahwa produknya keren — tujuannya membuktikan sistem ini benar-benar ada dan berjalan. Boleh tunjukkan bagian yang belum sempurna, itu justru sesuai instruksi rulebook.

> ⚠️ **ATURAN TEKNIS WAJIB (Auskulta = software only, bukan hardware-integrated):**
> - Wajib **double screen**: terminal DAN aplikasi (browser) terlihat BERSAMAAN di layar, dengan **timestamp** tampil.
> - Boleh **fast-forward** untuk melewati bagian nunggu loading, dan boleh tambah **voice-over**.
> - **DILARANG KERAS memotong (cut) video atau melakukan editing lain.** Ini harus rekam sekali jalan (continuous take). Kalau salah ngomong di tengah, ulang dari awal — bukan di-cut.
> - Latihan dulu 1-2 kali sebelum rekam final, supaya tidak perlu banyak ulang.

### [0:00 – 0:25] Intro
> "Halo, kami [ISI: Nama Tim], dan ini adalah Proof of Work untuk Auskulta — AI Machine Diagnosis Copilot untuk COMPFEST 18 AI Innovation Challenge, kategori Smart Manufacturing. Di video ini kami akan tunjukkan sistem kami benar-benar berjalan, dari kode sampai hasil akhir."

### [0:25 – 1:00] Tunjukkan repository
*(Screen share GitHub repo)*
> "Ini repository kami di GitHub, sudah public, dengan README, dokumentasi arsitektur di folder docs, dan riwayat commit yang menunjukkan proses pengembangan sistem ini — mulai dari deteksi visual, deteksi audio, sampai integrasi dengan LLM."

*(Scroll cepat struktur folder: backend/, frontend/, data/, docs/)*

### [1:00 – 1:45] Jalankan sistem dari nol
*(Screen share terminal)*
> "Sekarang kami jalankan sistem ini dari kondisi kosong, persis seperti yang akan dilakukan panitia."

```
docker compose down -v
docker compose up --build
```

> "Sistem otomatis menginstal semua dependency dan menjalankan tiga komponen AI: deteksi anomali visual, deteksi anomali audio, dan retrieval histori maintenance."

### [1:45 – 2:15] Buka aplikasi
*(Screen share browser, buka localhost:8000)*
> "Ini tampilan aplikasinya — sengaja kami buat sederhana: satu alur interaksi inti, upload video mesin, dapatkan satu laporan kesehatan mesin. Ini sesuai batasan MVP yang diminta panitia."

### [2:15 – 4:30] Demo alur utama
*(Upload video demo mesin — gunakan footage asli, bukan testsrc)*
> "Kami upload video mesin yang sedang beroperasi. Di belakang layar, sistem melakukan tiga hal sekaligus: menganalisis pola gerakan/getaran dari video, menganalisis suara mesin dari track audio, lalu mencari kejadian serupa di histori maintenance kami."

*(Tunggu hasil muncul, scroll ke setiap bagian sambil menjelaskan)*
> "Ini skor visual [ISI: sebutkan angka], ini skor audio [ISI: sebutkan angka]. Sistem menemukan [ISI: jumlah] kasus historis yang mirip — ini bagian yang kami sebut organizational memory. Sistem tidak langsung percaya, tapi mengecek dulu seberapa mirip kasusnya lewat bagian 'Kenapa diagnosis ini?' — ini reasoning trace yang menunjukkan evidence visual, audio, dan historis secara terpisah, plus tingkat confidence."

> "Berdasarkan evidence itu, LLM memberi diagnosis: [ISI: baca diagnosis], tingkat urgensi [ISI], estimasi downtime [ISI] jam, dan rekomendasi tindakan [ISI]."

### [4:30 – 5:15] Tunjukkan safety mechanism
> "Satu hal yang ingin kami tunjukkan: sistem ini tidak akan mengarang diagnosis kalau tidak ada evidence yang cukup mirip. Kalau kami coba video yang tidak punya kasus historis serupa..."

*(Kalau sempat, demo kasus dengan confidence rendah/insufficient evidence)*
> "...sistem akan bilang jujur bahwa ini kemungkinan kasus baru, bukan memaksakan jawaban. Ini kami desain sengaja di level kode, bukan cuma instruksi ke LLM, supaya diagnosis yang diberikan selalu bisa dipertanggungjawabkan."

### [5:15 – 6:15] Jujur soal keterbatasan saat ini
> "Kami juga ingin jujur soal kondisi sistem saat ini. Deteksi visual masih menggunakan baseline optical flow yang kami kalibrasi manual. Untuk audio, kami berhasil melatih model IsolationForest menggunakan 500 sampel suara mesin nyata dari dataset DCASE 2023 Task 2 — penerus akademik dari MIMII, karena dataset MIMII asli terlalu besar untuk diunduh dalam waktu kami. Knowledge base kami saat ini berisi 8 kasus, masih data yang kami susun sendiri berdasarkan skenario realistis, belum data pabrik sungguhan. Semua ini sudah kami rencanakan sebagai roadmap pengembangan lanjutan yang kami jelaskan di proposal."

### [6:15 – 7:00] Penutup
> "Itu adalah Proof of Work dari Auskulta — sistem yang benar-benar berjalan end-to-end, dari video mesin sampai diagnosis yang di-ground pada evidence nyata. Terima kasih."

---

# 2. PROMOTIONAL VIDEO (≤5 menit, YouTube public)

Format nama file: `COMPFEST 18 AIC: [Nama Tim] - Auskulta`

Tujuan video ini adalah meyakinkan penonton bahwa masalahnya nyata dan solusinya masuk akal — bukan penjelasan kode.

### [0:00 – 0:20] Hook
*(Visual: cuplikan mesin pabrik beroperasi, atau ilustrasi)*
> "Bayangkan sebuah mesin di pabrik mulai bergetar aneh. Operator yang melihatnya tidak yakin — apakah ini normal, atau tanda kerusakan besar yang akan datang?"

### [0:20 – 0:55] Problem
> "Jawabannya sering kali sudah pernah terjadi sebelumnya — tercatat di laporan maintenance lama, atau ada di ingatan teknisi senior. Tapi informasi itu terpecah: ada di PDF, di Excel, di WhatsApp, dan di kepala orang yang bisa saja resign kapan saja. Setiap gejala baru diperlakukan seperti kasus baru — padahal polanya sering berulang. Dan setiap keterlambatan diagnosis berarti downtime produksi yang mahal."

### [0:55 – 1:30] Solusi: perkenalkan Auskulta
*(Visual: logo/nama Auskulta muncul)*
> "Kami membangun Auskulta — AI yang mendiagnosis kesehatan mesin seperti dokter memeriksa pasien. Auskulta melihat gejala visual dari video mesin, mendengarkan suara mesin, lalu menelusuri rekam medis mesin — histori maintenance — sebelum memberi diagnosis. Hasilnya selalu bisa ditelusuri dasarnya, bukan tebakan."

### [1:30 – 3:00] Demo singkat
*(Screen recording aplikasi, dipercepat/diedit rapi)*
> "Caranya sederhana: upload satu video mesin yang sedang beroperasi..."

*(Tunjukkan hasil muncul: skor, evidence, diagnosis)*

> "...dan dalam hitungan detik, Auskulta memberi satu laporan lengkap: seberapa berisiko kondisi mesin ini, kasus serupa apa yang pernah terjadi, dan apa yang harus dilakukan teknisi sekarang."

### [3:00 – 3:50] Impact
> "Dengan Auskulta, waktu diagnosis yang tadinya butuh mencari-cari laporan lama atau menunggu teknisi senior, dipangkas jadi hitungan detik. Pengetahuan dari teknisi berpengalaman tetap tersimpan dan bisa diakses meski mereka sudah tidak lagi bekerja di sana. Dan yang penting: Auskulta tidak butuh sensor IoT mahal — cukup video biasa, bahkan dari HP — jadi bisa diadopsi pabrik skala menengah dengan biaya rendah."

### [3:50 – 4:30] Closing
> "Auskulta: melihat, mendengarkan, mengingat — supaya ketika pengalaman pergi, pengetahuan tidak ikut hilang."

*(Tampilkan nama tim, logo COMPFEST, dan tagline di layar penutup)*

---

# Checklist sebelum syuting

- [ ] Footage mesin ASLI sudah siap (bukan video generik) — minimal 1 normal, 1-2 "anomali"
- [ ] `.env` sudah diisi API key asli, dan sudah dites diagnosis benar-benar datang dari LLM (bukan fallback)
- [ ] Sudah dites angka skor yang keluar tidak aneh (lihat hasil kalibrasi Afif & Naufal)
- [ ] Istilah gejala yang diucapkan di skrip SAMA dengan istilah di `data/knowledge_base.json` (biar evidence yang muncul relevan)
- [ ] Rekam dengan tripod/penyangga stabil untuk footage mesin (bukan video-nya — video demo aplikasi cukup screen recording)
