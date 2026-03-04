# 💬 SentiDetect X — Twitter/X Sentiment Intelligence

**SentiDetect X** adalah aplikasi berbasis web untuk menganalisis sentimen komentar di Twitter/X secara real-time. Fokus utama aplikasi ini adalah mengidentifikasi dan mengelompokkan komentar **Negatif** atau **Sangat Negatif** ke dalam kategori "Buzzer Negatif". Aplikasi ini dirancang agar **100% siap di-deploy (Web/Cloud Ready)** dengan ketahanan terhadap pemblokiran sesi.

---

## ✨ Fitur Utama

- 🤖 **AI-Powered Sentiment**: Menggunakan model HuggingFace `twitter-xlm-roberta-base-sentiment` untuk akurasi tinggi dan dukungan multibahasa (termasuk Indonesia).
- 🛡️ **Anti-Block Web Fallback**: Dilengkapi dengan sistem *Fallback Scraper* menggunakan Syndication API. Jika token utama ditolak oleh Twitter karena perbedaan IP server Cloud, aplikasi akan **otomatis** beralih ke jalur alternatif publik tanpa error (Anti-crash HTTP 401/403).
- 🚨 **Buzzer Negatif Detection**: Klasifikasi khusus untuk komentar negatif yang berpotensi menjadi buzzer.
- 🌐 **Multilingual & Translation**: Deteksi bahasa otomatis dan terjemahan ke Bahasa Indonesia atau Inggris.
- 📊 **Interactive Dashboard**: Ringkasan statistik, chart sentimen, dan filter interaktif hasil analisis.
- 🌑 **Simple Dark UI**: Tampilan minimalis yang modern, responsif, cepat, dan mudah dibaca.

---

## 🛠️ Stack Teknologi

- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+)
- **AI/ML API**: HuggingFace Inference API (`requests`)
- **Data Scraping Utama**: Twitter GraphQL (via manual `auth_token` & `ct0`)
- **Data Scraping Cadangan**: Twitter Syndication API (Fallback Web) & BeautifulSoup4

---

## 🚀 Cara Instalasi

### 1. Prasyarat
Pastikan Anda sudah menginstal **Python 3.8+** di komputer Anda.

### 2. Clone atau Download Project
Buka terminal dan masuk ke folder project:
```shell
cd project_1
```

### 3. Instalasi Dependency
Instal library yang dibutuhkan menggunakan pip:
```shell
pip install -r requirements.txt
```

---

## 📖 Cara Penggunaan & Pengoperasian

Aplikasi ini mengandalkan Token Autentikasi yang diisi secara manual, sehingga cocok dan aman saat di-_hosting_ di server manapun.

### Langkah 1: Jalankan Aplikasi
1. Jalankan server Flask lokal Anda:
   ```shell
   python app.py
   ```
2. Buka Browser dan kunjungi `http://localhost:5000` (atau URL Vercel/Render Anda jika sudah di-deploy).

### Langkah 2: Ambil Token Akses `auth_token` & `ct0`
Anda perlu token dari akun Twitter pribadi Anda agar pencarian data tidak dibatasi:
1. Buka [https://twitter.com](https://twitter.com) di tab baru dan **Login** ke akun Anda.
2. Tekan tombol `F12` di keyboard untuk membuka mode **Developer Tools** (Inspect Element).
3. Buka tab **Application** (Chrome/Edge) atau **Storage** (Firefox).
4. Di panel kiri, cari bagian **Cookies** lalu klik `https://twitter.com`.
5. Temukan baris dengan nama `auth_token` dan salin (copy) isinya ke kolom **Twitter Auth Token** di website SentiDetect X.
6. Opsional tapi sangat disarankan: Temukan juga baris dengan nama `ct0` dan salin isinya ke kolom **Twitter CSRF Token (ct0)** di SentiDetect X.

### Langkah 3: Mulai Analisis
1. Di halaman SentiDetect X, masukkan kata kunci atau tagar yang ingin Anda analisis pada kolom "🔎 Topik / Hashtag".
2. Tentukan jumlah tweet maksimal yang ingin dianalisis (maks. 50).
3. Tekan tombol **🚀 Mulai Analisis Sentimen**.
4. Tunggu beberapa detik, analisis dan chart akan muncul di dashboard. Jika token utama memblokir trafik (misal karena IP cloud), SentiDetect X akan otomatis menggunakan mode cadangan anti-error!

---

## 📁 Struktur Project

```text
project_1/
├── app.py              # Backend Flask (Routing & Scraper & AI Call)
├── index.html          # Frontend utama (Antarmuka Utama)
├── requirements.txt    # Daftar library Python (Flask, requests, bs4, dsb)
├── README.md           # Dokumentasi ini
└── static/             # Assets statis website
    ├── css/style.css   # Styling (Simple Dark Theme)
    └── js/main.js      # Logika interaksi frontend (DOM/Fetch)
```

---

## ⚖️ Disclaimer
*Aplikasi ini dibuat untuk tujuan edukasi dan penelitian (Capstone Project). Token hanya disalurkan sementara di sisi server (RAM) untuk mengambil data saat diperlukan dan **sama sekali tidak disimpan ke database/file apapun**.*
