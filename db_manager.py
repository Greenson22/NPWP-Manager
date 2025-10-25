# db_manager.py
# Mengurus semua logika koneksi dan query database

import sqlite3
from config import DB_NAME, NAMA_TABEL, KOLOM_DB, FIELD_UNTUK_INSERT

# --- FUNGSI INIT (TETAP SAMA) ---
def init_db():
    """Membuat database dan tabel jika belum ada."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
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

# --- FUNGSI SAVE (TETAP SAMA) ---
def save_data(data: dict):
    """Menyimpan satu baris data (dari dict) ke database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        values_tuple = tuple(data.get(field) for field in FIELD_UNTUK_INSERT)
        placeholders = ', '.join(['?'] * len(FIELD_UNTUK_INSERT))
        fields = ', '.join(FIELD_UNTUK_INSERT)
        
        query = f"INSERT INTO {NAMA_TABEL} ({fields}) VALUES ({placeholders})"
        
        cursor.execute(query, values_tuple)
        conn.commit()
        conn.close()
        return True, "Data berhasil disimpan!"
        
    except sqlite3.IntegrityError:
        return False, f"Gagal menyimpan. NIK '{data.get('nik')}' mungkin sudah terdaftar."
    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"

# --- FUNGSI LOAD (TETAP SAMA) ---
def load_data():
    """Mengambil semua data dari database untuk ditampilkan di tabel."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        query = f"SELECT {', '.join(KOLOM_DB)} FROM {NAMA_TABEL} ORDER BY id DESC"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        
        headers = [kol.replace("_", " ").title() for kol in KOLOM_DB]
        
        return True, data, headers
    except Exception as e:
        return False, f"Gagal memuat data: {e}", []

# --- FUNGSI BARU ---

def get_data_by_id(id_to_fetch):
    """Mengambil satu baris data lengkap berdasarkan ID untuk diedit."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Ambil *semua* field (termasuk password) untuk form edit
        cursor.execute(f"SELECT * FROM {NAMA_TABEL} WHERE id = ?", (id_to_fetch,))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            return True, data
        else:
            return False, "Data tidak ditemukan."
            
    except Exception as e:
        return False, f"Error saat mengambil data by ID: {e}"

def update_data(id_to_update, data: dict):
    """Memperbarui satu baris data berdasarkan ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Buat string set query: "nama = ?, status = ?, ..."
        fields_to_set = ", ".join([f"{field} = ?" for field in FIELD_UNTUK_INSERT])
        
        # Buat tuple nilainya
        values_tuple = tuple(data.get(field) for field in FIELD_UNTUK_INSERT)
        
        # Tambahkan ID di akhir tuple untuk klausa WHERE
        values_tuple_with_id = values_tuple + (id_to_update,)
        
        query = f"UPDATE {NAMA_TABEL} SET {fields_to_set} WHERE id = ?"
        
        cursor.execute(query, values_tuple_with_id)
        conn.commit()
        conn.close()
        return True, "Data berhasil diperbarui!"
        
    except sqlite3.IntegrityError:
        return False, f"Gagal update. NIK '{data.get('nik')}' mungkin duplikat."
    except Exception as e:
        return False, f"Terjadi kesalahan saat update: {e}"

def delete_data(id_to_delete):
    """Menghapus satu baris data berdasarkan ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {NAMA_TABEL} WHERE id = ?", (id_to_delete,))
        conn.commit()
        conn.close()
        return True, "Data berhasil dihapus!"
    except Exception as e:
        return False, f"Gagal menghapus data: {e}"