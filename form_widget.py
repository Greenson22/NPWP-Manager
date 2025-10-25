# form_widget.py
# Berisi QWidget dengan TABS untuk formulir pendaftaran dan fitur AI

import os
import shutil
import platform
import subprocess
from pathlib import Path

# --- IMPOR PYQT ---
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QTextEdit, QPushButton, QMessageBox, QGroupBox, QDateEdit, QHBoxLayout,
    QListWidget, QListWidgetItem, QFileDialog, 
    QScrollArea, QApplication, QTabWidget
)
# --- IMPOR DIPERBARUI ---
from PyQt6.QtCore import QDate, QRegularExpression, pyqtSignal, Qt, QObject, QThread, pyqtSlot

from PyQt6.QtGui import QRegularExpressionValidator, QCursor

# --- IMPOR KUSTOM ---
import db_manager
from config import BASE_DOC_FOLDER
import gemini_parser 

# --- KELAS WORKER BARU (Tidak Berubah) ---
class GeminiWorker(QObject):
    """
    Worker thread untuk menjalankan panggilan API Gemini
    tanpa membekukan UI.
    """
    finished = pyqtSignal(bool, object) 
    progress = pyqtSignal(str)

    def __init__(self, image_paths: list[str]):
        super().__init__()
        self.image_paths = image_paths

    def run(self):
        """Tugas yang akan dijalankan di thread terpisah."""
        try:
            self.progress.emit("Memvalidasi API...")
            if not gemini_parser.api_is_configured:
                # Ambil pesan error yang sudah disimpan
                raise Exception(gemini_parser.api_init_error_message or "API Key belum dikonfigurasi.")
            
            self.progress.emit("Memuat gambar...")
            self.progress.emit(f"Mengirim {len(self.image_paths)} gambar ke Google Gemini ({gemini_parser.current_model_name})... Ini mungkin memakan waktu beberapa detik...")
            
            success, result = gemini_parser.extract_data_from_images(self.image_paths)
            
            self.finished.emit(success, result)
            
        except Exception as e:
            self.finished.emit(False, f"Terjadi kesalahan di thread: {e}")


# --- KELAS FORM WIDGET (DIPERBARUI DENGAN TABS) ---
class FormWidget(QWidget): 
    data_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.current_edit_id = None
        self.current_doc_folder = None
        self.files_to_add = set()
        self.files_to_remove = set()
        
        self.thread = None
        self.worker = None
        
        self.tab_widget = QTabWidget() 
        
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi User Interface (UI) untuk form."""
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget) 

        # --- Buat Tab 1: Fitur AI (Akan ditempatkan di kanan) ---
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        
        self.ai_fill_btn = QPushButton("🤖 Isi Otomatis dari KTP/KK...")
        self.ai_fill_btn.setStyleSheet("background-color: #0275d8; color: white; padding: 8px; border-radius: 4px;")
        self.ai_fill_btn.clicked.connect(self.on_ai_fill)
        ai_layout.addWidget(self.ai_fill_btn)
        
        group_log_ai = QGroupBox("Log Proses AI")
        layout_log_ai = QVBoxLayout()
        self.ai_log_output = QTextEdit()
        self.ai_log_output.setReadOnly(True)
        self.ai_log_output.append("Selamat datang! Silakan klik tombol 'Isi Otomatis' di atas.")
        layout_log_ai.addWidget(self.ai_log_output)
        group_log_ai.setLayout(layout_log_ai)
        ai_layout.addWidget(group_log_ai) 
        ai_layout.addStretch() 
        
        # --- Buat Tab 2: Formulir Pendaftaran (Akan ditempatkan di kiri) ---
        form_scroll_area = QScrollArea()
        form_scroll_area.setWidgetResizable(True)
        
        form_content_widget = QWidget()
        form_scroll_area.setWidget(form_content_widget)
        
        form_layout = QVBoxLayout(form_content_widget)

        # --- Logika Pengecekan API ---
        if not gemini_parser.api_is_configured:
            self.disable_ai_button(
                "API Key Belum Dikonfigurasi (Cek Menu File)"
            )
            self.ai_log_output.clear()
            self.ai_log_output.setStyleSheet("color: #D32F2F;") # Merah
            self.ai_log_output.append("--- KONEKSI API GAGAL ---")
            error_detail = gemini_parser.api_init_error_message or "Alasan tidak diketahui."
            self.ai_log_output.append(f"\nPesan Error:\n{error_detail}")
            self.ai_log_output.append("\n--- SOLUSI ---")
            self.ai_log_output.append("1. Buka menu 'File' -> 'Konfigurasi API Key...'.")
            self.ai_log_output.append("2. Masukkan API Key yang valid (misal dari Google AI Studio).")
            self.ai_log_output.append("3. Tutup dan jalankan ulang aplikasi ini setelah menyimpan Key.")

        nik_validator = QRegularExpressionValidator(QRegularExpression(r'\d{16}'))

        # --- Grup 1: Status Pendaftaran ---
        group_status = QGroupBox("Status Pendaftaran")
        layout_status = QFormLayout()
        self.status_input = QComboBox()
        self.status_input.addItems(["", "Berhasil", "Pengawasan", "Gagal"])
        self.keterangan_input = QLineEdit()
        layout_status.addRow("Status:", self.status_input)
        layout_status.addRow("Keterangan:", self.keterangan_input)
        group_status.setLayout(layout_status)
        
        # --- Grup 2: Data Diri ---
        group_data_diri = QGroupBox("Data Diri Pemohon")
        layout_data_diri = QFormLayout()
        self.nama_input = QLineEdit()
        self.nik_input = QLineEdit()
        self.nik_input.setValidator(nik_validator)
        self.nik_input.setPlaceholderText("16 digit NIK")
        self.nik_kk_input = QLineEdit()
        self.nik_kk_input.setValidator(nik_validator)
        self.nik_kk_input.setPlaceholderText("16 digit NIK Kepala Keluarga")
        self.no_kk_input = QLineEdit()
        self.no_kk_input.setValidator(nik_validator)
        self.no_kk_input.setPlaceholderText("16 digit Nomor Kartu Keluarga")
        self.tempat_lahir_input = QLineEdit()
        self.tanggal_lahir_input = QDateEdit()
        self.tanggal_lahir_input.setDate(QDate.currentDate().addYears(-20))
        self.tanggal_lahir_input.setCalendarPopup(True)
        self.tanggal_lahir_input.setDisplayFormat("dd MMMM yyyy")
        self.alamat_input = QTextEdit()
        self.alamat_input.setFixedHeight(80)
        self.pekerjaan_input = QLineEdit()
        self.nama_ibu_input = QLineEdit()
        layout_data_diri.addRow("Nama Lengkap:", self.nama_input)
        layout_data_diri.addRow("NIK:", self.nik_input)
        layout_data_diri.addRow("NIK Kepala Keluarga:", self.nik_kk_input)
        layout_data_diri.addRow("Nomor Kartu Keluarga:", self.no_kk_input)
        layout_data_diri.addRow("Tempat Lahir:", self.tempat_lahir_input)
        layout_data_diri.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        layout_data_diri.addRow("Alamat:", self.alamat_input)
        layout_data_diri.addRow("Pekerjaan:", self.pekerjaan_input)
        layout_data_diri.addRow("Nama Ibu Kandung:", self.nama_ibu_input)
        group_data_diri.setLayout(layout_data_diri)

        # --- Grup 3: Akun & Kontak ---
        group_akun = QGroupBox("Akun dan Kontak")
        layout_akun = QFormLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("contoh@email.com")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.no_hp_input = QLineEdit()
        self.no_hp_input.setPlaceholderText("08...")
        layout_akun.addRow("Email:", self.email_input)
        layout_akun.addRow("Password:", self.password_input)
        layout_akun.addRow("Nomor HP:", self.no_hp_input)
        group_akun.setLayout(layout_akun)

        # --- Grup 4: Manajemen Dokumen ---
        group_dokumen = QGroupBox("Manajemen Dokumen")
        layout_dokumen = QVBoxLayout()
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout_tombol_doc = QHBoxLayout()
        self.add_file_btn = QPushButton("Tambah File...")
        self.add_file_btn.clicked.connect(self.on_add_files)
        self.remove_file_btn = QPushButton("Hapus File Terpilih")
        self.remove_file_btn.clicked.connect(self.on_remove_file)
        self.open_folder_btn = QPushButton("Buka Folder")
        self.open_folder_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 6px; border-radius: 4px;")
        self.open_folder_btn.clicked.connect(self.on_open_folder)
        layout_tombol_doc.addWidget(self.add_file_btn)
        layout_tombol_doc.addWidget(self.remove_file_btn)
        layout_tombol_doc.addStretch()
        layout_tombol_doc.addWidget(self.open_folder_btn)
        layout_dokumen.addLayout(layout_tombol_doc)
        layout_dokumen.addWidget(self.file_list_widget)
        group_dokumen.setLayout(layout_dokumen)

        # --- Tombol Aksi ---
        layout_tombol = QHBoxLayout()
        self.simpan_btn = QPushButton("Simpan Data")
        self.simpan_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")
        self.simpan_btn.clicked.connect(self.simpan_data)
        self.bersihkan_btn = QPushButton("Bersihkan Form")
        self.bersihkan_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px;")
        self.bersihkan_btn.clicked.connect(self.bersihkan_form)
        layout_tombol.addWidget(self.bersihkan_btn)
        layout_tombol.addWidget(self.simpan_btn)

        # --- Tambahkan semua grup ke layout form ---
        form_layout.addWidget(group_status)
        form_layout.addWidget(group_data_diri)
        form_layout.addWidget(group_akun)
        form_layout.addWidget(group_dokumen)
        form_layout.addLayout(layout_tombol)

        # --- Tambahkan kedua tab ke QTabWidget ---
        self.tab_widget.addTab(form_scroll_area, "Formulir Pendaftaran")
        self.tab_widget.addTab(ai_tab, "🤖 Isi Otomatis (AI)")


    # --- FUNGSI AI DIPERBARUI (THREADING) ---
    
    @pyqtSlot(str)
    def update_ai_log(self, message: str):
        """Slot untuk menerima pesan dari worker dan menampilkannya."""
        self.ai_log_output.append(f"LOG: {message}")

    def on_ai_fill(self):
        """1. Mempersiapkan dan memulai worker thread."""
        
        if self.thread is not None and self.thread.isRunning():
            QMessageBox.warning(self, "Info", "Proses AI lain sedang berjalan. Harap tunggu.")
            return

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Gambar KTP dan Kartu Keluarga (Bisa >1 file)",
            "", 
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        
        if not files:
            return 

        self.ai_log_output.clear()
        self.ai_log_output.setStyleSheet("color: black;") 
        self.update_ai_log("Mempersiapkan thread...")
        self.ai_fill_btn.setEnabled(False)
        self.ai_fill_btn.setText("🤖 Memproses...")
        self.setCursor(QCursor(Qt.CursorShape.WaitCursor))

        self.thread = QThread()
        self.worker = GeminiWorker(files)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run) 
        self.worker.finished.connect(self.on_ai_finished) 
        self.worker.progress.connect(self.update_ai_log)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: print("Thread AI Selesai dan dibersihkan."))

        self.thread.start()

    @pyqtSlot(bool, object)
    def on_ai_finished(self, success: bool, result: object):
        """2. Dipanggil saat worker thread selesai."""
        
        self.enable_ai_button() 
        self.unsetCursor()
        
        if success:
            self.update_ai_log("Data berhasil diekstrak dari API.")
            QMessageBox.information(self, "Sukses", "Data berhasil digabungkan! Harap periksa kembali isiannya.")
            self.populate_form_with_ai_data(result)
            self.tab_widget.setCurrentIndex(0)
        else:
            self.update_ai_log(f"ERROR: {result}")
            self.ai_log_output.setStyleSheet("color: #D32F2F;") # Merah
            QMessageBox.critical(self, "Error AI", f"Gagal memproses gambar:\n{result}")

    # --- FUNGSI HELPER BARU UNTUK UI ---
    
    def enable_ai_button(self):
        """Mengaktifkan tombol AI."""
        self.ai_fill_btn.setEnabled(True)
        self.ai_fill_btn.setText("🤖 Isi Otomatis dari KTP/KK...")
        self.ai_fill_btn.setStyleSheet("background-color: #0275d8; color: white; padding: 8px; border-radius: 4px;")
        
    def disable_ai_button(self, text: str):
        """Menonaktifkan tombol AI dengan pesan."""
        self.ai_fill_btn.setEnabled(False)
        self.ai_fill_btn.setText(f"🤖 {text}")
        self.ai_fill_btn.setStyleSheet("background-color: #888; color: #ccc; padding: 8px; border-radius: 4px;")

    # --- FUNGSI LAIN (TIDAK BERUBAH) ---

    def populate_form_with_ai_data(self, data: dict):
        print(f"Mengisi form dengan data: {data}")
        if data.get('nama'): self.nama_input.setText(data.get('nama'))
        if data.get('nik'): self.nik_input.setText(data.get('nik'))
        if data.get('nik_kk'): self.nik_kk_input.setText(data.get('nik_kk'))
        if data.get('no_kk'): self.no_kk_input.setText(data.get('no_kk'))
        if data.get('tempat_lahir'): self.tempat_lahir_input.setText(data.get('tempat_lahir'))
        if data.get('alamat'): self.alamat_input.setPlainText(data.get('alamat'))
        if data.get('tanggal_lahir'):
            tgl = QDate.fromString(data.get('tanggal_lahir'), "yyyy-MM-dd")
            if not tgl.isValid():
                tgl = QDate.fromString(data.get('tanggal_lahir'), "dd-MM-yyyy")
            if tgl.isValid():
                self.tanggal_lahir_input.setDate(tgl)
            else:
                print(f"Format tanggal dari AI tidak valid: {data.get('tanggal_lahir')}")

    def on_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Pilih Dokumen", "", "Semua File (*.*)")
        if files:
            for file_path in files:
                self.files_to_add.add(file_path)
                item = QListWidgetItem(f"[BARU] {file_path}")
                self.file_list_widget.addItem(item)
    
    def on_remove_file(self):
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items: return
        for item in selected_items:
            item_text = item.text()
            if item_text.startswith("[BARU] "):
                self.files_to_add.discard(item_text.replace("[BARU] ", ""))
            else:
                self.files_to_remove.add(item_text)
            self.file_list_widget.takeItem(self.file_list_widget.row(item))

    def on_open_folder(self):
        if self.current_doc_folder and self.current_doc_folder.exists():
            path = str(self.current_doc_folder.resolve())
            try:
                if platform.system() == "Windows": os.startfile(path)
                elif platform.system() == "Darwin": subprocess.Popen(["open", path])
                else: subprocess.Popen(["xdg-open", path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Tidak bisa membuka folder: {e}")
        else:
            QMessageBox.information(self, "Info", "Folder belum ada. Simpan data.")

    def _populate_file_list(self):
        self.file_list_widget.clear()
        if self.current_doc_folder and self.current_doc_folder.exists():
            for file_path in self.current_doc_folder.iterdir():
                if file_path.is_file(): self.file_list_widget.addItem(file_path.name)
        
    def load_data_for_edit(self, user_id):
        self.bersihkan_form()
        success, data_row = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {data_row}")
            return
        self.nama_input.setText(data_row['nama'])
        self.status_input.setCurrentText(data_row['status'])
        self.keterangan_input.setText(data_row['keterangan'])
        self.nik_input.setText(data_row['nik'])
        self.nik_kk_input.setText(data_row['nik_kk'])
        self.no_kk_input.setText(data_row['no_kk'])
        self.tempat_lahir_input.setText(data_row['tempat_lahir'])
        tgl = QDate.fromString(data_row['tanggal_lahir'], "yyyy-MM-dd")
        self.tanggal_lahir_input.setDate(tgl)
        self.alamat_input.setPlainText(data_row['alamat'])
        self.pekerjaan_input.setText(data_row['pekerjaan'])
        self.nama_ibu_input.setText(data_row['nama_ibu'])
        self.email_input.setText(data_row['email'])
        self.password_input.setText(data_row['password'])
        self.no_hp_input.setText(data_row['no_hp'])
        self.current_edit_id = user_id
        self.simpan_btn.setText("Update Data")
        self.current_doc_folder = Path(BASE_DOC_FOLDER) / data_row['nik']
        self._populate_file_list()
        
        # Pastikan mulai di tab formulir (indeks 0)
        self.tab_widget.setCurrentIndex(0)

    def simpan_data(self):
        nik = self.nik_input.text()
        if not self.nama_input.text() or not nik:
            QMessageBox.warning(self, "Input Error", "Nama dan NIK wajib diisi!")
            return
        if not self.nik_input.hasAcceptableInput():
            QMessageBox.warning(self, "Input Error", "Format NIK tidak valid.")
            return
        data = {
            "nama": self.nama_input.text(),
            "status": self.status_input.currentText(),
            "keterangan": self.keterangan_input.text(),
            "nik": nik, "nik_kk": self.nik_kk_input.text(), "no_kk": self.no_kk_input.text(),
            "tempat_lahir": self.tempat_lahir_input.text(),
            "tanggal_lahir": self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            "alamat": self.alamat_input.toPlainText(),
            "pekerjaan": self.pekerjaan_input.text(),
            "nama_ibu": self.nama_ibu_input.text(),
            "email": self.email_input.text(), "password": self.password_input.text(), 
            "no_hp": self.no_hp_input.text(),
            "files_to_add": self.files_to_add, "files_to_remove": self.files_to_remove
        }
        if self.current_edit_id is None:
            success, message = db_manager.save_data(data)
        else:
            data['old_nik'] = self.current_doc_folder.name if self.current_doc_folder else nik
            success, message = db_manager.update_data(self.current_edit_id, data)
        if success:
            QMessageBox.information(self, "Sukses", message)
            self.bersihkan_form()
            self.data_saved.emit()
        else:
            QMessageBox.critical(self, "Database Error", message)

    def bersihkan_form(self):
        self.nama_input.clear()
        self.status_input.setCurrentIndex(0)
        self.keterangan_input.clear()
        self.nik_input.clear()
        self.nik_kk_input.clear()
        self.no_kk_input.clear()
        self.tempat_lahir_input.clear()
        self.tanggal_lahir_input.setDate(QDate.currentDate().addYears(-20))
        self.alamat_input.clear()
        self.pekerjaan_input.clear()
        self.nama_ibu_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.no_hp_input.clear()
        self.file_list_widget.clear()
        self.files_to_add.clear()
        self.files_to_remove.clear()
        self.current_doc_folder = None
        self.current_edit_id = None
        self.simpan_btn.setText("Simpan Data")
        
        # --- BLOK LOGIKA DIPERBARUI ---
        if gemini_parser.api_is_configured:
            self.ai_log_output.setStyleSheet("color: black;")
            self.ai_log_output.setText("Silakan klik tombol 'Isi Otomatis' di atas.")
            self.enable_ai_button()
        else:
            self.ai_log_output.clear()
            self.ai_log_output.setStyleSheet("color: #D32F2F;") # Merah
            self.ai_log_output.append("--- KONEKSI API GAGAL ---")
            error_detail = gemini_parser.api_init_error_message or "Alasan tidak diketahui."
            self.ai_log_output.append(f"\nPesan Error:\n{error_detail}")
            self.ai_log_output.append("\n--- SOLUSI ---")
            self.ai_log_output.append("1. Buka menu 'File' -> 'Konfigurasi API Key...'.")
            self.ai_log_output.append("2. Masukkan API Key yang valid (misal dari Google AI Studio).")
            self.ai_log_output.append("3. Tutup dan jalankan ulang aplikasi ini setelah menyimpan Key.")
            self.disable_ai_button("API Key Belum Dikonfigurasi")
        
        # --- PERUBAHAN DI SINI ---
        # Saat membersihkan form, kembali ke tab Formulir (indeks 0)
        self.tab_widget.setCurrentIndex(0)
        # ------------------