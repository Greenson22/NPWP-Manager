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
    QScrollArea, QCheckBox 
)
# --- IMPOR DIPERBARUI ---
from PyQt6.QtCore import QDate, QRegularExpression, pyqtSignal, pyqtSlot

from PyQt6.QtGui import QRegularExpressionValidator

# --- IMPOR KUSTOM ---
import db_manager
from config import BASE_DOC_FOLDER
# Hapus: import gemini_parser 

# Hapus: Seluruh kelas GeminiWorker


# --- KELAS FORM WIDGET (DIPERBARUI DENGAN TABS) ---
class FormWidget(QWidget): 
    data_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.current_edit_id = None
        self.current_doc_folder = None
        self.files_to_add = set()
        self.files_to_remove = set()
        
        # Hapus: self.thread = None
        # Hapus: self.worker = None
        
        # --- DAFTAR STATUS HUBUNGAN BARU ---
        self.STATUS_HUBUNGAN_LIST = [
            "", "Kepala Keluarga", "Suami", "Istri", "Anak", "Menantu", 
            "Orang tua", "Mertua", "Family Lain", "Pembantu", "Lainnya"
        ]
        
        # Hapus: self.tab_widget = QTabWidget() 
        
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi User Interface (UI) untuk form."""
        
        main_layout = QVBoxLayout(self)
        # Hapus: main_layout.addWidget(self.tab_widget) 

        # Hapus: Seluruh Tab 1: Fitur AI
        
        # --- Buat Formulir Pendaftaran (Sekarang layout utama) ---
        form_scroll_area = QScrollArea()
        form_scroll_area.setWidgetResizable(True)
        
        form_content_widget = QWidget()
        form_scroll_area.setWidget(form_content_widget)
        
        form_layout = QVBoxLayout(form_content_widget)

        # Hapus: Seluruh Logika Pengecekan API
        
        nik_validator = QRegularExpressionValidator(QRegularExpression(r'\d{16}'))

        # --- Grup 1: Status Pendaftaran ---
        group_status = QGroupBox("Status Pendaftaran")
        layout_status = QFormLayout()
        self.status_input = QComboBox()
        self.status_input.addItems(["", "Berhasil", "Pengawasan", "Gagal"])
        self.keterangan_input = QLineEdit()
        
        # --- WIDGET BARU ---
        self.catatan_input = QTextEdit()
        self.catatan_input.setFixedHeight(60) # Sedikit lebih pendek dari alamat
        self.catatan_input.setPlaceholderText("Tambahkan catatan internal di sini...")
        # --- AKHIR PERUBAHAN ---
        
        layout_status.addRow("Status:", self.status_input)
        layout_status.addRow("Keterangan:", self.keterangan_input)
        layout_status.addRow("Catatan:", self.catatan_input) # <-- Baris Ditambahkan
        
        group_status.setLayout(layout_status)
        
        # --- Grup 2: Data Diri ---
        group_data_diri = QGroupBox("Data Diri Pemohon")
        layout_data_diri = QFormLayout()
        self.nama_input = QLineEdit()
        
        # --- WIDGET BARU ---
        self.status_hubungan_input = QComboBox()
        self.status_hubungan_input.addItems(self.STATUS_HUBUNGAN_LIST)
        # --- AKHIR PERUBAHAN ---
        
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
        
        # --- BARIS BARU ---
        layout_data_diri.addRow("Status Hub. Keluarga:", self.status_hubungan_input)
        # --- AKHIR PERUBAHAN ---
        
        layout_data_diri.addRow("NIK:", self.nik_input)
        layout_data_diri.addRow("NIK Kepala Keluarga:", self.nik_kk_input)
        layout_data_diri.addRow("Nomor Kartu Keluarga:", self.no_kk_input)
        layout_data_diri.addRow("Tempat Lahir:", self.tempat_lahir_input)
        layout_data_diri.addRow("Tanggal Lahir:", self.tanggal_lahir_input)
        layout_data_diri.addRow("Alamat:", self.alamat_input)
        layout_data_diri.addRow("Pekerjaan:", self.pekerjaan_input)
        layout_data_diri.addRow("Nama Ibu Kandung:", self.nama_ibu_input)
        group_data_diri.setLayout(layout_data_diri)
        
        # --- KONEKSI SINYAL BARU ---
        self.status_hubungan_input.currentIndexChanged.connect(self.on_status_hubungan_changed)
        self.nik_input.textChanged.connect(self.on_nik_changed)
        # --- AKHIR PERUBAHAN ---

        # --- Grup 3: Akun & Kontak ---
        group_akun = QGroupBox("Akun dan Kontak")
        layout_akun = QFormLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("contoh@email.com")
        
        # --- PERUBAHAN PASSWORD ---
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.show_password_checkbox = QCheckBox("Tampilkan")
        self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_password_checkbox)
        # --- AKHIR PERUBAHAN ---
        
        self.no_hp_input = QLineEdit()
        self.no_hp_input.setPlaceholderText("08...")
        
        layout_akun.addRow("Email:", self.email_input)
        layout_akun.addRow("Password:", password_layout) # <-- BARIS DIGANTI
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

        # --- Tambahkan scroll area ke layout utama ---
        main_layout.addWidget(form_scroll_area)
        
        # Hapus: self.tab_widget.addTab(...)

    # --- FUNGSI BARU UNTUK PASSWORD ---
    @pyqtSlot(bool)
    def toggle_password_visibility(self, checked):
        """Mengubah mode tampilan QLineEdit password."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    # --- AKHIR FUNGSI BARU ---

    # Hapus: Seluruh method terkait AI
    # Hapus: update_ai_log
    # Hapus: on_ai_fill
    # Hapus: on_ai_finished
    # Hapus: enable_ai_button
    # Hapus: disable_ai_button
    

    # --- LOGIKA KUSTOM BARU UNTUK FORM ---
    
    def on_status_hubungan_changed(self):
        """Dipanggil saat QComboBox status hubungan berubah."""
        is_kepala_keluarga = (self.status_hubungan_input.currentText() == "Kepala Keluarga")
        
        self.nik_kk_input.setReadOnly(is_kepala_keluarga)
        if is_kepala_keluarga:
            # Jika Kepala Keluarga, salin NIK saat ini
            self.nik_kk_input.setText(self.nik_input.text())
        else:
            # Jika bukan, bersihkan dan buat dapat diedit
            self.nik_kk_input.clear()

    def on_nik_changed(self, text):
        """Dipanggil saat teks NIK berubah."""
        # Jika status adalah Kepala Keluarga, update NIK KK secara otomatis
        if self.status_hubungan_input.currentText() == "Kepala Keluarga":
            self.nik_kk_input.setText(text)

    # --- FUNGSI LAIN (DIPERBARUI) ---

    # Hapus: populate_form_with_ai_data

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
        self.catatan_input.setPlainText(data_row['catatan'] or "") # <-- Baris Ditambahkan
        
        # --- BARIS BARU ---
        self.status_hubungan_input.setCurrentText(data_row['status_hubungan'])
        # --- AKHIR PERUBAHAN ---
        
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
        
        # Hapus: self.tab_widget.setCurrentIndex(0)
        
        # --- PANGGILAN BARU ---
        # Panggil handler secara manual untuk mengatur state read-only NIK KK
        self.on_status_hubungan_changed()
        # --- AKHIR PERUBAHAN ---

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
            "catatan": self.catatan_input.toPlainText(), # <-- Baris Ditambahkan
            "status_hubungan": self.status_hubungan_input.currentText(), 
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
        self.catatan_input.clear() # <-- Baris Ditambahkan
        
        # --- BARIS BARU ---
        self.status_hubungan_input.setCurrentIndex(0)
        # --- AKHIR PERUBAHAN ---
        
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
        
        # --- BARIS BARU ---
        self.show_password_checkbox.setChecked(False) # Reset checkbox
        # --- AKHIR PERUBAHAN ---
        
        self.no_hp_input.clear()
        self.file_list_widget.clear()
        self.files_to_add.clear()
        self.files_to_remove.clear()
        self.current_doc_folder = None
        self.current_edit_id = None
        self.simpan_btn.setText("Simpan Data")
        
        # --- BARIS BARU ---
        # Pastikan NIK KK dapat diedit lagi
        self.nik_kk_input.setReadOnly(False)
        # --- AKHIR PERUBAHAN ---
        
        # Hapus: Seluruh blok logika if gemini_parser.api_is_configured:
        
        # Hapus: self.tab_widget.setCurrentIndex(0)