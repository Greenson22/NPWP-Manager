# Aplikasi Pendaftaran NPWP (Desktop)

Aplikasi desktop sederhana yang dibuat dengan Python dan PyQt6 untuk mengelola data pendaftaran NPWP dan mengarsipkan dokumen terkait.

## Fitur

* Manajemen data pendaftaran (CRUD - Create, Read, Update, Delete).
* Formulir pendaftaran dengan validasi NIK.
* Logika kustom untuk NIK Kepala Keluarga.
* Manajemen dokumen per pendaftar (Tambah/Hapus file, Buka folder).
* Tampilan tabel data dengan fitur pencarian (Nama/NIK) dan *context menu* (Edit, Hapus, Detail).
* Tampilan detail *read-only*.
* Fitur "Tampilkan Password" di tabel dan form.
* Bantuan AI Eksternal:
    * Salin *prompt* dan skema JSON untuk digunakan di alat eksternal (spt. Google AI Studio).
    * Impor hasil JSON untuk mengisi formulir secara otomatis.
* Dialog "Tentang Aplikasi" dengan informasi pengembang.

## Setup dan Instalasi

Pastikan Anda memiliki **Python 3.8** atau versi yang lebih baru terinstal di sistem Anda.

### 1. (Opsional) Buat Virtual Environment

Sangat disarankan untuk menggunakan *virtual environment* agar *package* proyek ini tidak tercampur dengan *package* Python global Anda.

Buka terminal atau Command Prompt, navigasi ke folder proyek ini, dan jalankan:

```sh
# Buat environment bernama 'venv'
python -m venv venv