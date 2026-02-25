# 💬 SentiDetect X — Twitter/X Sentiment Intelligence

**SentiDetect X** adalah aplikasi berbasis web untuk menganalisis sentimen komentar di Twitter/X secara real-time. Fokus utama aplikasi ini adalah mengidentifikasi dan mengelompokkan komentar **Negatif** atau **Sangat Negatif** ke dalam kategori "Buzzer Negatif".

---

## ✨ Fitur Utama

- 🤖 **AI-Powered Sentiment**: Menggunakan model HuggingFace `twitter-xlm-roberta-base-sentiment` untuk akurasi tinggi dan dukungan multibahasa (termasuk Indonesia).
- 🐦 **Auto Token Capture**: Fitur otomatisasi Playwright untuk mengambil `auth_token` Twitter langsung setelah login di browser.
- 🚨 **Buzzer Negatif Detection**: Klasifikasi khusus untuk komentar negatif yang berpotensi menjadi buzzer.
- 🌐 **Multilingual & Translation**: Deteksi bahasa otomatis dan terjemahan ke Bahasa Indonesia atau Inggris.
- 📊 **Interactive Dashboard**: Ringkasan statistik, chart sentimen, dan filter hasil analisis.
- 🌑 **Simple Dark UI**: Tampilan minimalis yang bersih, cepat, dan mudah dibaca.

---

## 🛠️ Stack Teknologi

- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+)
- **AI/ML**: `transformers` (HuggingFace), `torch`
- **Automation**: `playwright` (untuk auto-capture token)
- **Data Scraping**: Twitter API (Unofficial via `auth_token`)

---

## 🚀 Cara Instalasi

### 1. Prasyarat
Pastikan Anda sudah menginstal **Python 3.8+** di komputer Anda.

### 2. Clone atau Download Project
Buka terminal dan masuk ke folder project:
```powershell
cd project_1
```

### 3. Instalasi Dependency
Instal library yang dibutuhkan menggunakan pip:
```powershell
pip install -r requirements.txt
```

### 4. Setup Browser Automation (Playwright)
Agar fitur login otomatis berfungsi, instal driver browser Chromium:
```powershell
python -m playwright install chromium
```

---

## 📖 Cara Penggunaan

1. **Jalankan Aplikasi**:
   ```powershell
   python app.py
   ```
2. **Buka di Browser**:
   Masuk ke [http://localhost:5000](http://localhost:5000).
3. **Ambil Auth Token**:
   - Klik tombol **🐦 Login Twitter & Ambil Token**.
   - Sebuah browser Chrome akan terbuka. Silakan login ke akun Twitter/X Anda.
   - Setelah login berhasil, browser akan tertutup otomatis dan token akan terisi di form.
4. **Analisis**:
   - Masukkan topik atau hashtag (contoh: `#KneztVsSeablings`).
   - Tentukan jumlah tweet yang ingin diambil (maks 50).
   - Klik **Mulai Analisis Sentimen**.

---

## 📁 Struktur Project

```text
project_1/
├── app.py              # Backend Flask & Logika AI
├── index.html          # Frontend utama (Root)
├── requirements.txt    # Daftar library Python
├── README.md           # Dokumentasi ini
├── static/             # Assets statis
│   ├── css/style.css   # Styling (Simple Dark Theme)
│   └── js/main.js      # Logika interaksi frontend
└── task.md             # Catatan progres pengerjaan
```

---

## ⚖️ Disclaimer
*Aplikasi ini dibuat untuk tujuan edukasi dan penelitian (Capstone Project). Penggunaan `auth_token` dilakukan secara lokal di komputer pengguna dan tidak disimpan oleh sistem.*
