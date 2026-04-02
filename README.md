# SentiDetect X 🕵️‍♂️🐦
*Capstone Project — Sistem Deteksi Buzzer Negatif Twitter/X Berbasis Kecerdasan Buatan*

SentiDetect X adalah aplikasi web cerdas yang secara otomotis mengambil komentar dari platform X.com, lalu membedahnya satu per satu menggunakan teknologi Kecerdasan Buatan (Deep Learning) untuk mendeteksi *Buzzer* yang memprovokasi kemarahan (Sentimen Negatif Ekstrim).

Aplikasi ini menggunakan teknologi yang sepenuhnya dirancang untuk menembus batasan keamanan Twitter di tahun 2026 tanpa API berbayar.

---

## 🚀 Fitur Unggulan

1. **Scraping Siluman (Playwright Edge)**
   Twitter secara aktif memblokir program scraping (Twikit, Tweety, SnScrape) akibat keamanan `x-client-transaction-id` terbaru. SentiDetect mengakalinya dengan menggunakan *Playwright Headless* yang berjalan menumpang/menunggangi browser Microsoft Edge bawaan OS Anda secara diam-diam (tanpa memicu alarm Windows Firewall).
2. **Radar Profil Akurat (Deep JSON Parsing)**
   Aplikasi ini dilengkap algoritma pelacak struktural *rekursif* yang mutakhir. Model ini mampu mencari Nama dan *Username* akun bercentang biru maupun akun biasa tanpa terjebak pada format keamanan JSON Twitter yang terus berubah-ubah secara konstan.
3. **AI Konteks Penuh Kalimat (RoBERTa Transformer)**
   Bukan sekadar mencocokkan kata kotor secara primitif! Aplikasi ini menyusupkan komentar ke _w11wo/indonesian-roberta-base-sentiment-classifier_ milik API Router Hugging Face. Kecerdasan buatan ini membaca keseluruhan esensi kalimat persis seperti manusia seutuhnya.
4. **Kalibrasi Ambang Batas Otomatis (Threshold Tuning)**
   Model AI bawaan seringkali pesimis (menganggap kalimat biasa sebagai Negatif). Di `app.py`, kita telah menerapkan algoritma kalibrasi yang memaksa AI untuk melabeli ulang "Negatif Lemah" menjadi "Netral", dan mewajibkan skor keyakinan $> 95\%$ untuk mendeteksi "Sangat Negatif" (Buzzer).

---

## 🛠️ Prasyarat Instalasi (Tutorial Setup)

Sangat direkomendasikan meng-instal melalui Python Terminal *virtual environment* (`venv`).

### 1. Instalasi Modul
Buka Terminal/Command Prompt di dalam folder proyek ini, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 2. Pemasangan Rel Browser
Untuk memastikan robot Playwright bisa bekerja dan menyamar menjadi pengguna asli:
```bash
playwright install chromium
```
*(Meski terinstall chromium, aplikasi akan tetap memprioritaskan memakai `msedge` yang sudah terpasang rapi di OS Windows pengguna).*

### 3. Pengaturan API Key AI
1. Buat akun di [Hugging Face](https://huggingface.co/) (Gratis).
2. Pergi ke halaman `Settings` > `Access Tokens`.
3. Buat dan Salin API Token Anda.
4. Buka file `.env` di proyek ini, dan tempel token Anda di baris:
   ```env
   HF_TOKEN=hf_xxxxxx_token_anda_di_sini
   ```

---

## 💻 Cara Menggunakan Aplikasi SentiDetect

1. **Nyalakan Server**
   Di terminal VSCode atau folder Anda, eksekusi perintah:
   ```bash
   python app.py
   ```
2. **Akses Dashboard Interaktif**
   Aplikasi akan menyala sebagai Server Lokal pada alamat `http://localhost:5000` (silakan ditekan atau buka via browser Anda).

### 🔑 Tutorial: Mengambil `auth_token` Twitter/X

SentiDetect hanya butuh **satu kunci sakti** untuk bisa berkeliling di Twitter atas nama Anda:

1. Buka tab baru di browser dan pergi ke **[x.com](https://x.com)** (Pastikan Anda sudah login ke akun cadangan/akun utama Anda).
2. Klik kanan di mana saja di halaman Twitter tersebut, lalu pilih **Inspect Element** (atau tekan tombol `F12` di keyboard).
3. Di panel kanan/bawah yang muncul, cari tab/menu bernama **Application** (Jika tidak terlihat, klik tanda panah kecil `>>` di deretan menu atas).
4. Di panel kiri, klik tanda segitiga kecil di samping tulisan **Cookies**, lalu pilih **https://x.com**.
5. Di tengah jendela tersebut, akan tampil daftar kuki (cookies). Di kolom **Name**, carilah yang bernama: `auth_token`
6. Klik ganda (Double-click) pada **Value** dari *auth_token* tersebut, copy/salin semua kombinasi angka panjang tersebut.
7. Kembali ke aplikasi `localhost:5000` Anda, lalu tempel (*paste*) token ajaib itu ke dalam kotak pengisian UI!

*(Token ini memiliki kedaluwarsa yang sangat lama, jadi Anda bisa menggunakannya berhari-hari selagi Anda tidak me-logout akun Twitter di browser tersebut).*

---
**🏆 Dirancang khusus untuk Kebutuhan Kelulusan Capstone.**
*(Logika scraping & AI telah di-refactor guna performa maksimal)*
