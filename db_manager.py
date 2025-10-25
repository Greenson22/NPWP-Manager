# db_manager.py
# Mengurus semua logika koneksi dan query database

import sqlite3
import os
import shutil
from pathlib import Path
from config import DB_NAME, NAMA_TABEL, KOLOM_DB, FIELD_UNTUK_INSERT, BASE_DOC_FOLDER

def init_db():
    """Membuat database, tabel, dan folder dokumen utama jika belum ada."""
    try:
        # 1. Buat folder dokumen utama
        Path(BASE_DOC_FOLDER).mkdir(exist_ok=True)
        
        # 2. Buat database dan tabel
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
        print(f"Database {DB_NAME}, tabel {NAMA_TABEL}, dan folder {BASE_DOC_FOLDER} berhasil diinisialisasi.")
    except Exception as e:
        print(f"Error saat inisialisasi DB: {e}")

def save_data(data: dict):
    """Menyimpan data ke DB dan file ke filesystem."""
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

        # --- Logika File BARU ---
        nik = data.get('nik')
        folder_path = Path(BASE_DOC_FOLDER) / nik
        folder_path.mkdir(exist_ok=True) # Buat folder NIK
        
        files_to_add = data.get('files_to_add', set())
        for source_path_str in files_to_add:
            source_path = Path(source_path_str)
            dest_path = folder_path / source_path.name
            shutil.copy2(source_path, dest_path) # Salin file
        
        return True, "Data dan dokumen berhasil disimpan!"
        
    except sqlite3.IntegrityError:
        return False, f"Gagal menyimpan. NIK '{data.get('nik')}' mungkin sudah terdaftar."
    except Exception as e:
        return False, f"Terjadi kesalahan: {e}"

def update_data(id_to_update, data: dict):
    """Memperbarui data di DB dan mengelola file di filesystem."""
    try:
        # --- Logika Folder BARU ---
        new_nik = data.get('nik')
        old_nik = data.get('old_nik') # Kita dapat ini dari form
        
        folder_path = Path(BASE_DOC_FOLDER) / old_nik
        new_folder_path = Path(BASE_DOC_FOLDER) / new_nik
        
        # 1. Cek jika NIK berubah -> rename folder
        if old_nik != new_nik and folder_path.exists():
            try:
                os.rename(folder_path, new_folder_path)
                folder_path = new_folder_path # Update path untuk langkah selanjutnya
            except Exception as e:
                print(f"Gagal me-rename folder: {e}")
                # Lanjutkan meski gagal rename

        # 2. Update Database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        fields_to_set = ", ".join([f"{field} = ?" for field in FIELD_UNTUK_INSERT])
        values_tuple = tuple(data.get(field) for field in FIELD_UNTUK_INSERT)
        values_tuple_with_id = values_tuple + (id_to_update,)
        
        query = f"UPDATE {NAMA_TABEL} SET {fields_to_set} WHERE id = ?"
        
        cursor.execute(query, values_tuple_with_id)
        conn.commit()
        conn.close()

        # 3. Kelola File
        # Hapus file
        files_to_remove = data.get('files_to_remove', set())
        for filename in files_to_remove:
            file_to_del = folder_path / filename
            if file_to_del.exists():
                os.remove(file_to_del)
                
        # Tambah file baru
        files_to_add = data.get('files_to_add', set())
        for source_path_str in files_to_add:
            source_path = Path(source_path_str)
            dest_path = folder_path / source_path.name
            if not dest_path.exists(): # Hindari duplikat
                shutil.copy2(source_path, dest_path)
        
        return True, "Data dan dokumen berhasil diperbarui!"
        
    except sqlite3.IntegrityError:
        return False, f"Gagal update. NIK '{data.get('nik')}' mungkin duplikat."
    except Exception as e:
        return False, f"Terjadi kesalahan saat update: {e}"

def delete_data(id_to_delete):
    """Menghapus data dari DB dan folder terkait dari filesystem."""
    try:
        # 1. Ambil NIK *sebelum* menghapus data
        success, data_row = get_data_by_id(id_to_delete)
        if not success:
            return False, "Data tidak ditemukan untuk dihapus."
            
        nik = data_row['nik']
        folder_path = Path(BASE_DOC_FOLDER) / nik

        # 2. Hapus data dari Database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {NAMA_TABEL} WHERE id = ?", (id_to_delete,))
        conn.commit()
        conn.close()
        
        # 3. Hapus folder dan isinya
        if folder_path.exists():
            shutil.rmtree(folder_path)
            
        return True, "Data dan folder dokumen terkait berhasil dihapus!"
    except Exception as e:
        return False, f"Gagal menghapus data: {e}"
        
def get_data_by_id(id_to_fetch):
    # (Fungsi ini tidak berubah)
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {NAMA_TABEL} WHERE id = ?", (id_to_fetch,))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            return True, data
        else:
            return False, "Data tidak ditemukan."
            
    except Exception as e:
        return False, f"Error saat mengambil data by ID: {e}"

def load_data():
    # (Fungsi ini tidak berubah)
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