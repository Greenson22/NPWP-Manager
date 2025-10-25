# form_widget.py
# Berisi kelas QWidget untuk formulir pendaftaran

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QTextEdit, QPushButton, QMessageBox, QGroupBox, QDateEdit, QHBoxLayout
)
from PyQt6.QtCore import QDate, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QRegularExpressionValidator
import db_manager # Impor db_manager untuk menyimpan data

class FormWidget(QWidget):
    # Buat sinyal kustom
    # Sinyal ini akan 'memberi tahu' MainWindow bahwa data baru telah disimpan
    data_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi User Interface (UI) untuk form."""
        main_layout = QVBoxLayout(self)

        # Validator untuk NIK dan KK (16 digit angka)
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

        main_layout.addWidget(group_status)
        main_layout.addWidget(group_data_diri)
        main_layout.addWidget(group_akun)
        main_layout.addLayout(layout_tombol)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def simpan_data(self):
        """Validasi input UI, kumpulkan data, dan panggil db_manager."""
        
        # 1. Validasi Sederhana
        if not self.nama_input.text() or not self.nik_input.text():
            QMessageBox.warning(self, "Input Error", "Nama dan NIK wajib diisi!")
            return
            
        if not self.nik_input.hasAcceptableInput():
            QMessageBox.warning(self, "Input Error", "Format NIK tidak valid (harus 16 digit angka).")
            return
        
        # ... (tambahkan validasi lain jika perlu) ...

        # 2. Kumpulkan data ke dalam dictionary
        data = {
            "nama": self.nama_input.text(),
            "status": self.status_input.currentText(),
            "keterangan": self.keterangan_input.text(),
            "nik": self.nik_input.text(),
            "nik_kk": self.nik_kk_input.text(),
            "no_kk": self.no_kk_input.text(),
            "tempat_lahir": self.tempat_lahir_input.text(),
            "tanggal_lahir": self.tanggal_lahir_input.date().toString("yyyy-MM-dd"),
            "alamat": self.alamat_input.toPlainText(),
            "pekerjaan": self.pekerjaan_input.text(),
            "nama_ibu": self.nama_ibu_input.text(),
            "email": self.email_input.text(),
            "password": self.password_input.text(), 
            "no_hp": self.no_hp_input.text()
        }
        
        # 3. Kirim data ke db_manager
        success, message = db_manager.save_data(data)
        
        # 4. Tampilkan feedback
        if success:
            QMessageBox.information(self, "Sukses", message)
            self.bersihkan_form()
            self.data_saved.emit() # PENTING: Kirim sinyal!
        else:
            QMessageBox.critical(self, "Database Error", message)

    def bersihkan_form(self):
        """Mengosongkan semua bidang input."""
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