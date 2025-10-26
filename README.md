# Aplikasi Pendaftaran NPWP (Asisten Entri Data)

![Versi Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-PyQt6-green?logo=qt)
![Database](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite&logoColor=white)

Sebuah aplikasi desktop internal yang dibangun dengan Python, PyQt6, dan SQLite untuk membantu mengelola, mengarsipkan, dan mempercepat proses entri data pendaftaran NPWP.

![Tampilan Utama Aplikasi NPWP Manager](https://user-images.githubusercontent.com/username/repo/raw/main/assets/screenshots/daftar_data.png)
*(Catatan: Ganti URL gambar di atas dengan path ke gambar `daftar_data.png` di repositori Anda)*

---

## 🎯 Latar Belakang & Konteks

Proyek ini berawal dari tantangan nyata yang dihadapi di komunitas desa, di mana banyak warga yang awam teknologi membutuhkan bantuan untuk mendaftarkan NPWP melalui portal online (coretax).

Proses bantuan awal dilakukan secara manual, dengan data pemohon tersebar di catatan pribadi, chat WhatsApp, dan folder yang tidak terorganisir. Hal ini membuat proses entri data ke portal pajak menjadi lambat, tidak efisien, dan sangat rentan terhadap kesalahan (error).

Aplikasi ini dikembangkan untuk menyelesaikan kekacauan tersebut.

## ⚠️ Peringatan Penting

> **Ini adalah Alat Bantu Internal (Asisten Pribadi).**
>
> Aplikasi ini **TIDAK TERHUBUNG** secara resmi dengan API portal pajak (coretax). Tujuannya murni untuk mengelola dan mengorganisir semua data serta dokumen pemohon secara terstruktur *sebelum* operator (saya) melakukan entri data secara manual ke portal resmi.

---

## ✨ Fitur Utama

Aplikasi ini mengubah proses yang kacau menjadi alur kerja yang terstruktur.

* **🗃️ Manajemen Data Lengkap (CRUD):**
    Menyediakan fungsionalitas penuh untuk **Menambah** data pemohon baru, **Melihat** semua data dalam tabel, **Mengedit** data yang sudah ada, dan **Menghapus** data dengan aman.

* **🔍 Pencarian Instan & Keamanan:**
    Halaman utama dilengkapi fitur pencarian *real-time* berdasarkan **Nama** atau **NIK**. Data sensitif seperti password disamarkan secara default di dalam tabel untuk menjaga privasi.

* **📂 Arsip Dokumen Cerdas:**
    Saat menyimpan data baru, aplikasi secara otomatis **membuatkan folder khusus** untuk setiap pemohon (berdasarkan NIK mereka). Folder ini digunakan untuk menyimpan dokumen penting seperti scan KTP, KK, dan file pendukung lainnya.

* **🤖 Bantuan Entri Data (AI Assist):**
    Untuk mempercepat entri data awal dari dokumen fisik (KTP/KK), aplikasi ini memiliki tab "Bantuan AI" yang berfungsi dalam dua langkah:
    1.  **Menyediakan Prompt:** Memberikan instruksi dan skema JSON yang dirancang khusus untuk disalin ke model AI eksternal (seperti Google AI Studio).
    2.  **Mengimpor Hasil:** Menerima hasil JSON dari AI tersebut dan secara otomatis mengisi (auto-fill) semua field yang relevan di formulir pendaftaran.

* **📄 Tampilan Detail Lengkap:**
    Memungkinkan pengguna melihat rincian lengkap setiap pemohon dalam mode *read-only*, termasuk melihat daftar dokumen yang tersimpan dan tombol untuk **"Membuka Folder Dokumen"** terkait langsung di file explorer.

* **📓 Fitur Catatan Internal:**
    Setiap data pemohon memiliki field "Catatan" terpisah untuk menyimpan informasi kontekstual yang tidak termasuk dalam formulir resmi (misal: "Masih menunggu scan KK terbaru").

---

## 🖼️ Galeri & Tampilan

| Formulir Entri Data | Bantuan AI (Ekstraksi Data) | Detail & Manajemen Dokumen |
| :---: | :---: | :---: |
| ![Formulir Entri Data](https://user-images.githubusercontent.com/username/repo/raw/main/assets/screenshots/entri_data.png) | ![Bantuan AI](https://user-images.githubusercontent.com/username/repo/raw/main/assets/screenshots/bantuan_ai.png) | ![Detail & Manajemen Dokumen](https://user-images.githubusercontent.com/username/repo/raw/main/assets/screenshots/management_document.png) |

*(Catatan: Ganti URL gambar di atas dengan path ke gambar di repositori Anda)*

---

## 🚀 Teknologi yang Digunakan

* **Bahasa:** Python 3
* **Antarmuka (GUI):** PyQt6
* **Database:** SQLite 3 (Lokal)

---

## 📦 Instalasi & Menjalankan

Aplikasi ini dirancang untuk dijalankan di lingkungan desktop.

1.  **Clone repositori ini:**
    ```bash
    git clone [https://github.com/username/nama-repo.git](https://github.com/username/nama-repo.git)
    cd nama-repo
    ```

2.  **Buat dan aktifkan virtual environment (Opsional tapi direkomendasikan):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (Di Windows: venv\Scripts\activate)
    ```

3.  **Install dependensi yang diperlukan:**
    (Jika Anda memiliki `requirements.txt`, gunakan `pip install -r requirements.txt`. Jika tidak, install manual):
    ```bash
    pip install PyQt6
    ```

4.  **Jalankan aplikasi:**
    Database (`pendaftaran_npwp.db`) dan folder dokumen (`dokumen_npwp/`) akan dibuat secara otomatis saat aplikasi dijalankan pertama kali.
    ```bash
    python main.py
    ```

---

## 👨‍💻 Pengembang

* **Frendy Rikal Gerung, S.Kom.**
* [LinkedIn](https://linkedin.com/in/frendy-rikal-gerung-bb450b38a/)