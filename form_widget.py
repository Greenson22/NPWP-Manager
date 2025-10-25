# form_widget.py
# Berisi kelas QWidget untuk formulir pendaftaran

import os
import shutil
import platform
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QTextEdit, QPushButton, QMessageBox, QGroupBox, QDateEdit, QHBoxLayout,
    QListWidget, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import QDate, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
import db_manager
from config import BASE_DOC_FOLDER

class FormWidget(QWidget):
    data_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_edit_id = None
        self.current_doc_folder = None
        # Set untuk melacak file yang akan ditambah/dihapus
        self.files_to_add = set()
        self.files_to_remove = set()
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi User Interface (UI) untuk form."""
        main_layout = QVBoxLayout(self)

        nik_validator = QRegularExpressionValidator(QRegularExpression(r'\d{16}'))

        # --- Grup 1: Status Pendaftaran (Sama) ---
        group_status = QGroupBox("Status Pendaftaran")
        layout_status = QFormLayout()
        self.status_input = QComboBox()
        self.status_input.addItems(["", "Berhasil", "Pengawasan", "Gagal"])
        self.keterangan_input = QLineEdit()
        layout_status.addRow("Status:", self.status_input)
        layout_status.addRow("Keterangan:", self.keterangan_input)
        group_status.setLayout(layout_status)
        
        # --- Grup 2: Data Diri (Sama) ---
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

        # --- Grup 3: Akun & Kontak (Sama) ---
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

        # --- Grup 4: Manajemen Dokumen (BARU) ---
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

        # --- Tombol Aksi (Sama) ---
        layout_tombol = QHBoxLayout()
        self.simpan_btn = QPushButton("Simpan Data")
        self.simpan_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")
        self.simpan_btn.clicked.connect(self.simpan_data)
        self.bersihkan_btn = QPushButton("Bersihkan Form")
        self.bersihkan_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px; border-radius: 4px;")
        self.bersihkan_btn.clicked.connect(self.bersihkan_form)
        layout_tombol.addWidget(self.bersihkan_btn)
        layout_tombol.addWidget(self.simpan_btn)

        main_layout.addWidget(group_status)
        main_layout.addWidget(group_data_diri)
        main_layout.addWidget(group_akun)
        main_layout.addWidget(group_dokumen) # Tambahkan grup baru
        main_layout.addLayout(layout_tombol)
        
        self.setLayout(main_layout)

    # --- FUNGSI DOKUMEN BARU ---

    def on_add_files(self):
        """Buka dialog untuk memilih satu atau beberapa file."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Dokumen untuk Ditambahkan",
            "", # Mulai dari direktori terakhir
            "Semua File (*.*);;PDF (*.pdf);;Images (*.jpg *.png)"
        )
        
        if files:
            for file_path in files:
                self.files_to_add.add(file_path)
                item = QListWidgetItem(f"[BARU] {file_path}")
                self.file_list_widget.addItem(item)
    
    def on_remove_file(self):
        """Menghapus file yang dipilih dari list."""
        selected_items = self.file_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Peringatan", "Pilih file yang ingin dihapus.")
            return

        for item in selected_items:
            item_text = item.text()
            if item_text.startswith("[BARU] "):
                # Ini file baru, hapus dari 'files_to_add'
                source_path = item_text.replace("[BARU] ", "")
                self.files_to_add.discard(source_path)
            else:
                # Ini file lama, tandai untuk dihapus
                filename = item_text
                self.files_to_remove.add(filename)
            
            self.file_list_widget.takeItem(self.file_list_widget.row(item))

    def on_open_folder(self):
        """Membuka folder dokumen orang ini di file explorer."""
        if self.current_doc_folder and self.current_doc_folder.exists():
            path = str(self.current_doc_folder.resolve())
            try:
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin": # macOS
                    subprocess.Popen(["open", path])
                else: # Linux
                    subprocess.Popen(["xdg-open", path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Tidak bisa membuka folder: {e}")
        else:
            QMessageBox.information(self, "Info", "Folder belum ada. Simpan data terlebih dahulu.")

    def _populate_file_list(self):
        """Helper untuk mengisi list file saat mode edit."""
        self.file_list_widget.clear()
        if self.current_doc_folder and self.current_doc_folder.exists():
            for file_path in self.current_doc_folder.iterdir():
                if file_path.is_file():
                    self.file_list_widget.addItem(file_path.name)
        
    # --- FUNGSI DIPERBARUI ---
    
    def load_data_for_edit(self, user_id):
        """Ambil data dari DB dan isi form untuk mode edit."""
        self.bersihkan_form()
        
        success, data_row = db_manager.get_data_by_id(user_id)
        if not success:
            QMessageBox.critical(self, "Error", f"Gagal memuat data: {data_row}")
            return

        # Isi semua field
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

        # Set mode edit
        self.current_edit_id = user_id
        self.simpan_btn.setText("Update Data")
        
        # --- Logika File BARU ---
        self.current_doc_folder = Path(BASE_DOC_FOLDER) / data_row['nik']
        self._populate_file_list() # Isi list file yang ada


    def simpan_data(self):
        """Kumpulkan data, termasuk data file, lalu panggil db_manager."""
        
        # 1. Validasi
        nik = self.nik_input.text()
        if not self.nama_input.text() or not nik:
            QMessageBox.warning(self, "Input Error", "Nama dan NIK wajib diisi!")
            return
        if not self.nik_input.hasAcceptableInput():
            QMessageBox.warning(self, "Input Error", "Format NIK tidak valid (harus 16 digit angka).")
            return
        
        # 2. Kumpulkan data
        data = {
            "nama": self.nama_input.text(),
            "status": self.status_input.currentText(),
            "keterangan": self.keterangan_input.text(),
            "nik": nik,
            "nik_kk": self.nik_kk_input.text(),
            "no_kk": self.no_kk_input.text(),
            "tempat_lahir": self.tempat_lahir_input.text(),
            "tanggal_lahir": self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            "alamat": self.alamat_input.toPlainText(),
            "pekerjaan": self.pekerjaan_input.text(),
            "nama_ibu": self.nama_ibu_input.text(),
            "email": self.email_input.text(),
            "password": self.password_input.text(), 
            "no_hp": self.no_hp_input.text(),
            # --- Data File BARU ---
            "files_to_add": self.files_to_add,
            "files_to_remove": self.files_to_remove
        }
        
        # 3. Kirim data
        if self.current_edit_id is None:
            # Mode Tambah Baru (INSERT)
            success, message = db_manager.save_data(data)
        else:
            # Mode Edit (UPDATE)
            # Kirim NIK lama jika ada, untuk rename folder
            data['old_nik'] = self.current_doc_folder.name if self.current_doc_folder else nik
            success, message = db_manager.update_data(self.current_edit_id, data)
        
        # 4. Tampilkan feedback
        if success:
            QMessageBox.information(self, "Sukses", message)
            self.bersihkan_form()
            self.data_saved.emit()
        else:
            QMessageBox.critical(self, "Database Error", message)

    def bersihkan_form(self):
        """Mengosongkan semua bidang input dan reset mode."""
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
        
        # --- Reset File BARU ---
        self.file_list_widget.clear()
        self.files_to_add.clear()
        self.files_to_remove.clear()
        self.current_doc_folder = None
        
        # Reset mode
        self.current_edit_id = None
        self.simpan_btn.setText("Simpan Data")