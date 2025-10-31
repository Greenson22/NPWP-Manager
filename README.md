
# Aplikasi Pendaftaran NPWP

Aplikasi desktop sederhana yang dibangun dengan Python dan PyQt6 untuk mengelola data pendaftaran (seperti NPWP), mengarsipkan dokumen terkait, dan dilengkapi fitur Bantuan AI untuk mempercepat entri data.

## 🚀 Link Download

[**Unduh versi rilis (Windows) di sini**](https://drive.google.com/file/d/1sHDBQVAgeIVpPKBlbTeZemXDqZ0PJUFr/view?usp=sharing)

-----

## 📸 Tampilan Aplikasi

*(Catatan: Anda harus mengganti placeholder di bawah ini dengan screenshot aplikasi Anda yang sebenarnya agar terlihat profesional.)*

| Tampilan Utama (Daftar Data) | Formulir Pendaftaran |
| :---: | :---: |
|  |  |
| *Tampilan utama untuk melihat, mencari, dan mengelola semua data.* | *Formulir untuk menambah atau mengedit data pendaftar.* |

| Bantuan AI (Eksternal) | Tampilan Detail (Read-only) |
| :---: | :---: |
|  |  |
| *Tab untuk menyalin prompt AI dan mengimpor hasil JSON.* | *Tampilan detail data yang aman (read-only) dan daftar dokumen.* |

-----

## ✨ Fitur Utama

Aplikasi ini menyediakan fungsionalitas CRUD (Create, Read, Update, Delete) yang lengkap serta beberapa fitur canggih:

  * **Manajemen Data Lengkap:** Tambah, edit, lihat, dan hapus data pendaftar.
  * **Manajemen Dokumen Terintegrasi:**
      * Secara otomatis membuat folder khusus (menggunakan NIK) untuk setiap pendaftar di dalam folder `dokumen_npwp`.
      * Memungkinkan pengguna untuk menambah atau menghapus file (seperti scan KTP, KK, dll.) dari formulir.
      * Folder akan otomatis terhapus saat data pendaftar dihapus.
      * Folder akan otomatis di-rename jika NIK pendaftar diubah.
  * **Pencarian Cepat:** Mencari data secara instan di tabel utama berdasarkan **Nama** atau **NIK**.
  * **Bantuan AI (Eksternal):**
      * Menyediakan *system prompt* dan skema JSON yang sudah jadi untuk disalin.
      * Pengguna dapat menggunakan prompt ini di alat AI eksternal (seperti Google AI Studio) dengan mengunggah gambar KTP/KK.
      * Hasil JSON dari AI dapat di-paste kembali ke aplikasi untuk **mengisi formulir secara otomatis**.
  * **Tampilan Detail Aman:** Melihat rincian data pendaftar dalam mode *read-only* untuk mencegah kesalahan edit.
  * **Keamanan Password:**
      * Password disembunyikan (mode `••••••••`) di tabel utama dan formulir detail.
      * Terdapat *checkbox* untuk menampilkan atau menyembunyikan password saat diperlukan.
  * **Database Lokal:** Menggunakan SQLite (`pendaftaran_npwp.db`) untuk penyimpanan data yang portabel, ringan, dan tidak memerlukan server.
  * **Dialog "Tentang":** Menyertakan jendela *About* kustom dengan informasi pengembang.

-----

## ⚙️ Cara Menggunakan

### Untuk Pengguna (Menjalankan Aplikasi)

1.  Unduh file dari [link download di atas](https://drive.google.com/file/d/1sHDBQVAgeIVpPKBlbTeZemXDqZ0PJUFr/view?usp=sharing).
2.  Ekstrak file `.zip` (jika ada).
3.  Jalankan file `main.exe` (atau nama file eksekusi utamanya).
4.  Aplikasi siap digunakan. Database (`pendaftaran_npwp.db`) dan folder dokumen (`dokumen_npwp`) akan dibuat secara otomatis di direktori yang sama dengan aplikasi saat pertama kali dijalankan.

### Untuk Developer (Menjalankan dari Kode Sumber)

1.  Pastikan Anda memiliki **Python 3** terinstal.
2.  Clone repositori ini atau unduh kode sumbernya.
3.  Buat dan aktifkan *virtual environment*:
    ```bash
    # Buat venv
    python -m venv venv

    # Aktifkan di Windows
    .\venv\Scripts\activate

    # Aktifkan di macOS/Linux
    source venv/bin/activate
    ```
4.  Instal dependensi yang diperlukan:
    ```bash
    pip install PyQt6
    ```
5.  Jalankan aplikasi:
    ```bash
    python code/main.py
    ```

-----

## 🛠️ Teknologi yang Digunakan

  * **Python 3:** Bahasa pemrograman utama.
  * **PyQt6:** *Framework* untuk membangun antarmuka pengguna (UI) desktop.
  * **SQLite3:** *Library* bawaan Python untuk manajemen database lokal.

-----

## 🗂️ Struktur Proyek

Berikut adalah penjelasan singkat mengenai file-file utama dalam proyek ini:

  * `code/main.py`: **Titik masuk utama aplikasi.** Mengelola `QMainWindow`, `QStackedWidget` untuk navigasi antar halaman, dan menu bar.
  * `code/form_widget.py`: **Formulir Pendaftaran.** Berisi UI dan logika untuk menambah data baru, mengedit data, serta tab "Bantuan AI".
  * `code/view_widget.py`: **Tampilan Daftar Data.** Berisi `QTableWidget` untuk menampilkan semua data, lengkap dengan fitur pencarian dan menu klik kanan (Edit, Hapus, Detail).
  * `code/detail_widget.py`: **Tampilan Detail.** Berisi UI *read-only* untuk menampilkan rincian lengkap satu pendaftar dan daftar dokumennya.
  * `code/db_manager.py`: **Manajer Database.** Mengurus semua logika database (koneksi, `init_db`, `save_data`, `update_data`, `delete_data`, `load_data`) dan manajemen file/folder (membuat, me-rename, menghapus folder dokumen).
  * `code/about_dialog.py`: Jendela kustom "Tentang Aplikasi" yang menampilkan info pengembang.
  * `code/config.py`: File konfigurasi untuk menyimpan konstanta seperti nama database, nama tabel, dan daftar kolom.
  * `assets/pictures/profile.jpg`: Gambar profil yang digunakan di dialog "Tentang".

-----

## 👨‍💻 Tentang Pengembang

Aplikasi ini dibuat dan dikembangkan oleh:
**Frendy Rikal Gerung, S.Kom.**
(Lulusan Sarjana Komputer dari Universitas Negeri Manado)