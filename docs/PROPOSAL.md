# CATATAN UNTUK TIM (hapus bagian ini sebelum export ke PDF)

- Struktur ini mengikuti persis bagian wajib di Rulebook AIC COMPFEST 18: Nama Kelompok & Judul, Latar Belakang, Tujuan & Manfaat, Metodologi (3 sub-bagian), Metode Lain Pendukung Keputusan, Kesimpulan.
- Batas halaman: **20 halaman**, TIDAK termasuk cover, daftar pustaka, dan lampiran.
- **Halaman Links wajib diletakkan SEBELUM cover**, di halaman tersendiri, dan halaman ini TIDAK dihitung dalam batas 20 halaman.
- Isi semua bagian yang ditandai `[ISI: ...]` sebelum submit.
- Jangan lupa: seluruh anggota tim wajib isi form Repository Secrets: https://forms.gle/FnmBbGkpq6JhcZi79 (wajib diisi walau aplikasi tidak butuh secrets).
- Deadline: Selasa, 25 Agustus 2026, 23.55 WIB (bukan 23.59).

---

# HALAMAN LINKS
*(halaman ini diletakkan sebelum cover proposal, tidak dihitung dalam batas maksimum halaman)*

**GitHub Repository:**
https://github.com/Ramane-Vision/auskulta

**Proof of Work Video:**
[ISI: link YouTube unlisted, format nama file "COMPFEST 18 AIC: PROOF OF WORK - [Nama Tim] - Auskulta"]

**Promotional Video:**
[ISI: link YouTube public, format nama file "COMPFEST 18 AIC: [Nama Tim] - Auskulta"]

---

# COVER

**AUSKULTA**
AI Machine Diagnosis Copilot: Integrasi Visual-Audio Anomaly Detection dan Organizational Memory untuk Diagnosis Kesehatan Mesin yang Ter-grounding pada Evidence Historis

AI Innovation Challenge — COMPFEST 18
Track: Smart Manufacturing
Tema: *AI for the Backbone of the Economy*

Tim: [ISI: Nama Tim]
Anggota:
1. [ISI: Nama — Peran]
2. [ISI: Nama — Peran]
3. [ISI: Nama — Peran]
4. [ISI: Nama — Peran]
5. [ISI: Nama — Peran]

Agustus 2026

---

# 1. Nama Kelompok dan Judul/Nama Inovasi

**Nama Kelompok:** [ISI: Nama Tim]

**Judul Inovasi:** AUSKULTA — AI Machine Diagnosis Copilot Berbasis Integrasi Visual-Audio Anomaly Detection dan Organizational Memory untuk Smart Manufacturing

**Tagline:** *AI yang mendiagnosis kesehatan mesin seperti dokter memeriksa pasien — melihat gejala, mendengarkan suara, lalu menelusuri rekam medis sebelum memberi diagnosis.*

---

# 2. Latar Belakang

Industri manufaktur merupakan salah satu tulang punggung (backbone) perekonomian Indonesia, namun masih menghadapi tantangan struktural berupa inefisiensi produksi yang bersumber dari downtime mesin yang tidak terduga. Berdasarkan pola umum di industri manufaktur, downtime yang tidak direncanakan dapat menyebabkan kerugian produksi yang signifikan per jam, terutama pada lini produksi yang saling bergantung (interdependent production line), di mana kegagalan satu mesin dapat menghentikan seluruh alur produksi.

Salah satu akar masalah dari lambatnya respons terhadap gejala awal kerusakan mesin adalah **fragmentasi pengetahuan operasional**. Pada praktiknya, mesin yang mulai menunjukkan gejala tidak normal — getaran berlebih, gerakan tersendat, suara yang berubah — sebenarnya sering kali sudah pernah mengalami kejadian serupa di masa lalu. Informasi mengenai penyebab dan solusinya biasanya *sudah ada*, tetapi tersebar di berbagai sumber yang tidak terintegrasi: SOP dalam bentuk PDF, laporan maintenance dalam spreadsheet, catatan WhatsApp antar-shift, hingga pengalaman tak tertulis dari teknisi senior. Ketika teknisi berpengalaman tersebut resign atau pensiun, pengetahuan kritis ini turut hilang, dan setiap gejala baru diperlakukan seolah-olah kasus baru — padahal polanya sering kali berulang.

Di sisi lain, solusi predictive maintenance konvensional yang umum ditemukan di industri maupun kompetisi inovasi biasanya mengandalkan sensor IoT khusus yang mahal dan sulit diadopsi oleh pabrik skala menengah, atau model computer vision yang hanya mendeteksi anomali tanpa mampu menjelaskan *mengapa* anomali tersebut terjadi dan *apa* yang sebaiknya dilakukan. Akibatnya, operator di lapangan tetap harus melakukan proses pencarian manual — bertanya ke senior, mencari SOP, membuka arsip laporan lama — sebelum bisa mengambil keputusan, sementara mesin terus dalam kondisi berisiko.

Kesenjangan inilah yang mendasari pengembangan **Auskulta**: sebuah AI copilot yang tidak hanya mendeteksi anomali dari sinyal visual dan audio mesin secara real-time, tetapi juga secara otomatis menelusuri histori maintenance yang relevan (organizational memory), sehingga diagnosis yang dihasilkan **selalu dapat ditelusuri dasarnya** — bukan tebakan model yang tidak dapat dipertanggungjawabkan.

---

# 3. Tujuan dan Manfaat Pengembangan

## 3.1 Tujuan

1. Membangun sistem deteksi dini anomali mesin yang memanfaatkan dua modalitas sinyal (visual dan audio) tanpa memerlukan sensor IoT khusus, cukup menggunakan video yang dapat direkam dari kamera biasa/HP.
2. Mengubah dokumentasi operasional yang terfragmentasi (SOP, laporan maintenance, catatan insiden) menjadi *organizational memory* yang dapat ditelusuri secara otomatis dan relevan terhadap gejala yang sedang terjadi.
3. Menghasilkan diagnosis yang **ter-grounding pada evidence historis nyata**, bukan jawaban bebas dari model bahasa, untuk meminimalkan risiko halusinasi dan meningkatkan kepercayaan pengguna di lapangan.
4. Menyediakan solusi dengan biaya adopsi rendah — dapat dijalankan sebagai aplikasi web sederhana tanpa investasi infrastruktur IoT tambahan — sehingga dapat diakses oleh pabrik skala menengah yang menjadi mayoritas pelaku industri manufaktur nasional.

## 3.2 Manfaat

**Bagi operasional pabrik:**
- Mempercepat waktu diagnosis dari yang semula membutuhkan pencarian manual (bertanya ke senior, membuka arsip) menjadi hitungan detik.
- Mengurangi ketergantungan pada individu (teknisi senior) sebagai satu-satunya sumber pengetahuan diagnosis.
- Memungkinkan tindakan preventif lebih dini sebelum anomali berkembang menjadi kerusakan besar dan downtime tak terduga.

**Bagi keberlanjutan pengetahuan organisasi:**
- Pengetahuan operasional dari teknisi berpengalaman tetap terlestarikan dan dapat diakses meski personel yang bersangkutan sudah tidak lagi bekerja di perusahaan tersebut.
- Setiap kejadian baru yang berhasil didiagnosis dapat memperkaya knowledge base untuk kasus-kasus berikutnya.

**Bagi nilai ekonomi dan bisnis:**
- Target pengguna adalah divisi maintenance pabrik manufaktur skala menengah (tekstil, F&B, elektronik, otomotif) yang memiliki arsip data maintenance namun belum memanfaatkannya secara digital.
- Model adopsi berbiaya rendah (tanpa hardware tambahan) membuka peluang penetrasi pasar yang lebih luas dibanding solusi predictive maintenance berbasis sensor IoT yang mahal.
- Potensi model bisnis: SaaS berlangganan bulanan per lini produksi, dengan value proposition utama pada pengurangan downtime dan retensi pengetahuan operasional.

---

# 4. Metodologi

## 4.1 Alur dalam Memperoleh Dataset

Auskulta menggunakan tiga jenis data dengan strategi perolehan yang berbeda sesuai kebutuhan masing-masing komponen AI:

**a. Data visual (deteksi anomali gerakan/getaran).**
Komponen visual pada tahap MVP dirancang tidak memerlukan dataset berlabel — pendekatan yang digunakan adalah analisis optical flow yang bersifat unsupervised, sehingga dapat langsung bekerja pada video apa pun tanpa proses training. Untuk pengembangan lanjutan, tim merencanakan pemanfaatan dataset video industri publik maupun rekaman video mesin sungguhan pada tahap final untuk memvalidasi dan mengkalibrasi ambang batas skor anomali.

**b. Data audio (deteksi anomali suara mesin).**
Pada tahap penyisihan, komponen audio menggunakan pendekatan heuristik berbasis fitur spektral (MFCC, spectral flatness, zero-crossing rate) yang juga tidak memerlukan data berlabel. Untuk peningkatan akurasi di tahap final, tim merencanakan pelatihan model anomaly detection menggunakan dataset publik **MIMII (Malfunctioning Industrial Machine Investigation and Inspection)** dari Hitachi — dataset rekaman suara mesin industri (fan, pump, valve, slider) dalam kondisi normal dan anomali yang lazim digunakan pada riset predictive maintenance berbasis audio.

**c. Data organizational memory (histori maintenance).**
Untuk tahap penyisihan, tim menyusun dataset sintetis berisi 8 catatan histori maintenance yang merepresentasikan struktur data riil yang lazim ditemukan di pabrik (gejala, penyebab, tindakan yang diambil, estimasi downtime, tanggal kejadian). Struktur dan pola data ini disusun berdasarkan skenario kejadian umum di industri manufaktur (bearing degradation, belt misalignment, motor overheat, kebocoran hidrolik, dsb.) agar representatif terhadap kondisi nyata. Pada tahap final, dataset ini direncanakan diperluas dan/atau digantikan dengan data riil dari mitra industri (jika tersedia melalui proses wawancara/kolaborasi).

## 4.2 Alur Pengembangan Model (per fitur)

**Fitur 1 — Visual Anomaly Detection.**
Video di-sampling menjadi rangkaian frame (maksimum 90 frame per video), dikonversi ke grayscale, kemudian dihitung dense optical flow (algoritma Farneback) antar-frame berurutan untuk mengestimasi pergerakan piksel. Rasio variansi terhadap rata-rata magnitude flow dijadikan sebagai *indeks getaran* — semakin tidak konsisten pergerakannya, semakin tinggi indikasi anomali. Nilai ini dinormalisasi menjadi skor 0–1. Modul ini juga menyediakan hook opsional untuk model deteksi objek visual (YOLO) yang telah di-fine-tune untuk mendeteksi kejadian visual spesifik (asap, percikan api) sebagai pengembangan lanjutan.

**Fitur 2 — Audio Anomaly Detection.**
Audio diekstrak dari track suara video, kemudian dihitung fitur spektral: MFCC (representasi timbre suara), spectral flatness (mengukur seberapa "berisik" spektrum suara), dan zero-crossing rate (mengukur perubahan tanda sinyal, berkorelasi dengan suara kasar/tidak stabil). Ketiga fitur digabung melalui fungsi heuristik terbobot menjadi skor anomali audio. Modul ini dirancang sebagai **sinyal sekunder yang bersifat best-effort**: apabila proses ekstraksi audio gagal (video tanpa audio track, dependency tidak tersedia), sistem otomatis melanjutkan analisis hanya dengan sinyal visual tanpa menggagalkan keseluruhan proses — desain ini sengaja dipilih agar keandalan sistem end-to-end tidak bergantung pada satu titik kegagalan tunggal.

**Fitur 3 — Organizational Memory Retrieval.**
Setiap catatan histori maintenance direpresentasikan sebagai teks gabungan (nama mesin, gejala, penyebab), lalu diindeks menggunakan TF-IDF vectorization. Ketika ada gejala baru (dari catatan visual dan/atau audio), sistem membentuk query teks dari catatan tersebut dan mencari kejadian historis paling mirip menggunakan cosine similarity, mengembalikan top-k kejadian paling relevan beserta skor kemiripannya.

**Fitur 4 — LLM Diagnosis Fusion.**
Skor visual dan audio digabung secara terbobot (visual berbobot lebih besar karena selalu tersedia dan tervalidasi, audio berbobot lebih kecil karena sifatnya best-effort) menjadi satu *risk score*. Skor ini, beserta seluruh evidence historis yang berhasil di-retrieve, dikirim ke LLM dengan instruksi sistem yang ketat: model **wajib mendasarkan jawabannya pada evidence yang diberikan** dan dilarang mengarang penyebab yang tidak didukung data. Keluaran LLM berupa JSON terstruktur (diagnosis, tingkat urgensi, estimasi downtime, rekomendasi tindakan, daftar evidence yang benar-benar dirujuk). Sebagai mitigasi risiko (API tidak tersedia/gagal), sistem memiliki mekanisme fallback berbasis aturan yang tetap merujuk pada evidence yang ditemukan, sehingga sistem tidak pernah gagal total dalam memberikan output.

## 4.3 Alur Integrasi Model ke Environment Kode

Seluruh komponen AI diimplementasikan sebagai modul Python independen (`vision.py`, `audio.py`, `knowledge.py`, `diagnosis.py`) yang disatukan melalui satu endpoint FastAPI (`POST /api/analyze`), sesuai dengan batasan ruang lingkup MVP penyisihan AIC 2026 (satu input, satu output, tanpa kebutuhan autentikasi maupun dashboard analitik lanjutan). Arsitektur modular ini dipilih agar setiap komponen dapat dikembangkan, diuji, dan ditingkatkan secara independen oleh anggota tim yang berbeda tanpa saling mengganggu.

Aplikasi dikemas menggunakan Docker Compose untuk memastikan proses instalasi dan menjalankan sistem dapat direproduksi secara konsisten di lingkungan mana pun, sesuai dengan ketentuan teknis rulebook. Frontend diimplementasikan sebagai satu halaman web sederhana (vanilla HTML/JS) yang berfokus pada satu alur interaksi inti: unggah video → tampilkan laporan kesehatan mesin, tanpa fitur pelengkap yang berada di luar cakupan MVP yang diminta panitia.

---

# 5. Metode-Metode Lain yang Mendukung Keputusan Pengembangan

**Mengapa TF-IDF, bukan model embedding berbasis deep learning?**
Untuk skala data awal (puluhan hingga ratusan catatan maintenance), TF-IDF dengan cosine similarity memberikan hasil retrieval yang cukup akurat tanpa memerlukan API embedding eksternal (mengurangi biaya operasional dan dependency terhadap layanan pihak ketiga) dan dapat berjalan sepenuhnya offline dengan latensi sangat rendah. Pendekatan ini dipilih secara sadar sebagai *baseline yang robust*, dengan jalur peningkatan (upgrade path) ke model embedding semantik apabila volume data bertambah besar dan kebutuhan pemahaman makna yang lebih dalam (bukan sekadar kemiripan kata) menjadi krusial.

**Mengapa optical flow, bukan model deep learning untuk deteksi visual?**
Model deep learning untuk klasifikasi anomali visual membutuhkan dataset berlabel spesifik per jenis mesin, yang tidak tersedia pada tahap penyisihan. Optical flow dipilih karena bersifat generik (bekerja pada video mesin apa pun tanpa training), cepat dihitung, dan cukup untuk mendeteksi indikasi umum ketidakstabilan gerakan/getaran — sambil tetap menyediakan jalur integrasi model deteksi objek terlatih sebagai pengembangan lanjutan tanpa perlu mengubah arsitektur sistem secara keseluruhan.

**Mengapa audio didesain sebagai sinyal best-effort, bukan wajib?**
Ekstraksi dan analisis audio memiliki lebih banyak titik kegagalan teknis dibanding analisis visual (ketergantungan pada codec, ketersediaan track audio, dependency sistem seperti ffmpeg). Untuk menjaga keandalan demo dan penggunaan sistem secara keseluruhan, tim secara sengaja mendesain audio sebagai lapisan tambahan yang meningkatkan kualitas diagnosis ketika tersedia, namun tidak menjadi single point of failure bagi keseluruhan sistem.

**Mengapa instruksi evidence-grounding yang ketat pada LLM?**
Diagnosis di ranah industri memiliki konsekuensi nyata (biaya perbaikan, downtime, keselamatan kerja). Tim memilih untuk membatasi LLM secara eksplisit agar hanya menjawab berdasarkan evidence yang diberikan, alih-alih membiarkannya menjawab bebas, sebagai bentuk mitigasi risiko halusinasi dan agar setiap rekomendasi dapat dipertanggungjawabkan sumbernya kepada teknisi di lapangan.

**Mengapa ruang lingkup MVP sengaja dibatasi?**
Tim secara sadar mengikuti batasan ruang lingkup yang ditetapkan panitia (satu alur interaksi inti, tanpa dashboard analitik lanjutan maupun sistem otentikasi kompleks) agar pengembangan dapat fokus pada validasi inti permasalahan dan solusi AI, bukan pada aspek engineering pelengkap yang tidak memengaruhi pembuktian konsep.

---

# 6. Kesimpulan

Auskulta menjawab persoalan nyata di industri manufaktur Indonesia — hilangnya pengetahuan operasional kritis dan lambatnya respons terhadap gejala awal kerusakan mesin — melalui pendekatan AI yang menggabungkan tiga lapisan kemampuan: deteksi anomali visual, deteksi anomali audio, dan penelusuran organizational memory berbasis histori maintenance. Berbeda dengan pendekatan predictive maintenance konvensional yang berhenti pada "mesin akan rusak", Auskulta memberikan diagnosis yang dapat dipertanggungjawabkan karena selalu ter-grounding pada evidence historis nyata, sekaligus tidak memerlukan investasi sensor IoT khusus sehingga dapat diadopsi oleh pabrik skala menengah dengan biaya rendah.

Pada tahap penyisihan ini, tim telah membangun MVP fungsional yang mendemonstrasikan keseluruhan alur — dari input video mesin hingga laporan diagnosis yang ter-evidence — beserta repository kode sumber, dokumentasi arsitektur, dan video demonstrasi. Ke depan, apabila lolos ke tahap final, tim berencana meningkatkan akurasi model audio melalui pelatihan pada dataset MIMII, memperluas knowledge base dengan data maintenance riil dari mitra industri, serta menambahkan kapabilitas deteksi visual spesifik melalui model terlatih — sehingga Auskulta dapat berkembang dari pembuktian konsep menjadi solusi yang siap diadopsi industri secara nyata.

---

# LAMPIRAN
*(tidak dihitung dalam batas halaman)*

- [ISI: screenshot antarmuka aplikasi]
- [ISI: contoh output laporan diagnosis]
- [ISI: struktur repository]

# DAFTAR PUSTAKA
*(tidak dihitung dalam batas halaman)*

- [ISI: referensi dataset MIMII, jika dikutip langsung]
- [ISI: referensi pendukung data industri/statistik yang dipakai di Latar Belakang, jika ada]
