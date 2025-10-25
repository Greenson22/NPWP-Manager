<div align="center">

# 🗂️ Aplikasi Pendaftaran NPWP

**Aplikasi desktop sederhana untuk mengelola data pendaftaran NPWP dan mengarsipkan dokumen terkait.**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

</div>

---

Aplikasi ini dibuat dengan **Python** dan **PyQt6** sebagai antarmuka *front-end*, dengan **SQLite** sebagai database lokal untuk menyimpan semua data pendaftaran.

## ✨ Fitur Utama

* **📝 Manajemen Data (CRUD)**: Buat, Baca, Perbarui, dan Hapus data pendaftaran dengan mudah.
* **✅ Validasi Formulir**: Dilengkapi validasi NIK (16 digit) dan logika kustom untuk sinkronisasi NIK Kepala Keluarga.
* **🗂️ Manajemen Dokumen**: Unggah, hapus, dan buka folder dokumen yang terkait dengan setiap pendaftar.
* **📊 Tampilan Tabel Interaktif**:
    * Cari data secara dinamis berdasarkan **Nama** atau **NIK**.
    * Klik kanan untuk menu konteks (Lihat Detail, Edit, Hapus).
    * Sembunyikan/tampilkan password di tabel.
* **🔒 Tampilan Detail**: Mode *read-only* untuk meninjau data tanpa risiko mengedit.
* **🤖 Bantuan AI Eksternal**:
    * **Salin Prompt**: Hasilkan dan salin *system prompt* beserta skema JSON untuk digunakan di alat eksternal (seperti Google AI Studio).
    * **Impor JSON**: Tempelkan hasil JSON dari AI untuk mengisi data formulir secara otomatis.
* **ℹ️ Tentang Aplikasi**: Dialog "Tentang Aplikasi" yang menampilkan informasi pengembang dan tautan kontak.

---

## 🚀 Instalasi dan Setup

Pastikan Anda memiliki **Python 3.8** atau versi yang lebih baru terinstal di sistem Anda.

### 1. (Opsional) Buat Virtual Environment

Sangat disarankan untuk menggunakan *virtual environment* agar *package* proyek ini tidak tercampur dengan *package* Python global Anda.

Buka terminal atau Command Prompt, navigasi ke folder proyek ini, dan jalankan:

```sh
# Buat environment bernama 'venv'
python -m venv venv