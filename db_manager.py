# db_manager.py
# Mengurus semua logika koneksi dan query database

import sqlite3
from config import DB_NAME, NAMA_TABEL, KOLOM_DB, FIELD_UNTUK_INSERT

def init_db():
    """Membuat database dan tabel jika belum ada."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Membuat field query secara dinamis
        query_buat_tabel = f'''
        CREATE TABLE IF NOT EXISTS {NAMA_TABEL} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            status TEXT,
            keterangan TEXT,
            nik TEXT UNIQUE NOT NULL,
            nik_kk TEXT,
            no_kk TEXT,
            tempat_lahir TEXT,
            tanggal_lahir TEXT,
            alamat TEXT,
            pekerjaan TEXT,
            nama_ibu TEXT,
            email TEXT,
            password TEXT,
            no_hp TEXT
        )
        '''
        cursor.execute(query_buat_tabel)
        conn.commit()
        conn.close()
        print(f"Database {DB_NAME} dan tabel {NAMA_TABEL} berhasil diinisialisasi.")
    except Exception as e:
        print(f"Error saat inisialisasi DB: {e}")

def save_data(data: dict):
    """Menyimpan satu baris data (dari dict) ke database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Membuat tuple nilai berdasarkan urutan di FIELD_UNTUK_INSERT
        values_tuple = tuple(data.get(field) for field in FIELD_UNTUK_INSERT)
        
        placeholders = ', '.join(['?'] * len(FIELD_UNTUK_INSERT))
        fields = ', '.join(FIELD_UNTUK_INSERT)
        
        query = f'''
        INSERT INTO {NAMA_TABEL} (
            {fields}
        ) VALUES ({placeholders})
        '''
        
        cursor.execute(query, values_tuple)
        conn.commit()
        conn.close()
        return True, "Data berhasil disimpan!"
        
    except sqlite3.IntegrityError:
        return False, f"Gagal menyimpan. NIK '{data.get('nik')}' mungkin sudah terdaftar."
    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"

def load_data():
    """Mengambil semua data dari database untuk ditampilkan di tabel."""
    try:
        conn = sqlite3.connect(DB_NAME)
        # Menggunakan Row Factory agar bisa memanggil data berdasarkan nama kolom
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        query = f"SELECT {', '.join(KOLOM_DB)} FROM {NAMA_TABEL} ORDER BY id DESC"
        cursor.execute(query)
        data = cursor.fetchall() # Ini akan menjadi list dari objek sqlite3.Row
        conn.close()
        
        # Membuat header yang 'cantik'
        headers = [kol.replace("_", " ").title() for kol in KOLOM_DB]
        
        return True, data, headers
    except Exception as e:
        return False, f"Gagal memuat data: {e}", []