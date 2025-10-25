# config.py
# Menyimpan konstanta konfigurasi

DB_NAME = 'pendaftaran_npwp.db'
NAMA_TABEL = 'pendaftaran'

# Kolom yang akan ditampilkan di tabel (sengaja tanpa password)
# --- DIPERBARUI ---
KOLOM_DB = [
    "id", "nama", "status", "keterangan", "status_hubungan", "nik", "nik_kk", 
    "no_kk", "tempat_lahir", "tanggal_lahir", "alamat", 
    "pekerjaan", "nama_ibu", "email", "password", "no_hp", "catatan" # <-- Ditambahkan
]

# Daftar lengkap field untuk INSERT ke DB
# --- DIPERBARUI ---
FIELD_UNTUK_INSERT = [
    'nama', 'status', 'keterangan', 'status_hubungan', 'nik', 'nik_kk', 'no_kk', 
    'tempat_lahir', 'tanggal_lahir', 'alamat', 'pekerjaan', 
    'nama_ibu', 'email', 'password', 'no_hp', 'catatan' # <-- Ditambahkan
]

# --- BARIS BARU ---
# Nama folder utama untuk menyimpan semua dokumen
BASE_DOC_FOLDER = 'dokumen_npwp'