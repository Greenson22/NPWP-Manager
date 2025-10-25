# about_dialog.py
# Berisi QDialog kustom untuk halaman "Tentang Aplikasi"

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QWidget
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # --- Informasi dari file about_page.dart ---
        DEV_NAME = "Frendy Rikal Gerung, S.Kom."
        DEV_TITLE = "Lulusan Sarjana Komputer dari Universitas Negeri Manado"
        DEV_LINKEDIN = "https://linkedin.com/in/frendy-rikal-gerung-bb450b38a/"
        DEV_EMAIL = "mailto:frendydev1@gmail.com"
        
        # --- Informasi untuk Aplikasi NPWP ---
        APP_NAME = "Aplikasi Pendaftaran NPWP"
        APP_DESC = (
            "Aplikasi desktop sederhana (dibuat dengan Python dan PyQt6) "
            "untuk mengelola data pendaftaran, mengarsipkan dokumen, "
            "dan menyediakan bantuan entri data."
        )

        self.setWindowTitle(f"Tentang {APP_NAME}")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)

        # --- Info Aplikasi ---
        group_app = QFrame()
        group_app.setFrameShape(QFrame.Shape.StyledPanel)
        layout_app = QVBoxLayout(group_app)
        
        lbl_app_name = QLabel(APP_NAME)
        font_app = lbl_app_name.font()
        font_app.setPointSize(14)
        font_app.setBold(True)
        lbl_app_name.setFont(font_app)
        lbl_app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_app_desc = QLabel(APP_DESC)
        lbl_app_desc.setWordWrap(True)
        lbl_app_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_app.addWidget(lbl_app_name)
        layout_app.addWidget(lbl_app_desc)
        
        main_layout.addWidget(group_app)

        # --- Info Pengembang (dari file .dart) ---
        group_dev = QFrame()
        group_dev.setFrameShape(QFrame.Shape.StyledPanel)
        layout_dev = QHBoxLayout(group_dev) # Horizontal layout

        # --- PERUBAHAN DI SINI ---
        # Memuat foto profil dari asset
        lbl_photo = QLabel()
        lbl_photo.setFixedSize(80, 80)
        
        pixmap = QPixmap("assets/pictures/profile.jpg")
        if pixmap.isNull():
            # Fallback jika gambar gagal dimuat
            lbl_photo.setStyleSheet(
                "background-color: #ddd; border-radius: 40px; "
                "border: 2px solid #aaa; color: #888;"
            )
            lbl_photo.setText("Gagal\Muat")
        else:
            # Tampilkan gambar
            pixmap = pixmap.scaled(
                80, 80, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            )
            lbl_photo.setPixmap(pixmap)
            # Atur stylesheet untuk membuatnya bulat
            lbl_photo.setStyleSheet(
                "border: 2px solid #aaa; border-radius: 40px;"
            )
            
        lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # --- AKHIR PERUBAHAN ---
        
        # Info Teks
        layout_text = QVBoxLayout()
        
        lbl_dev_name = QLabel(DEV_NAME)
        font_name = lbl_dev_name.font()
        font_name.setPointSize(12)
        font_name.setBold(True)
        lbl_dev_name.setFont(font_name)
        
        lbl_dev_title = QLabel(DEV_TITLE)
        lbl_dev_title.setWordWrap(True)
        
        # Links
        lbl_links = QLabel(
            f'<a href="{DEV_LINKEDIN}">LinkedIn</a> | '
            f'<a href="{DEV_EMAIL}">Email</a>'
        )
        lbl_links.setOpenExternalLinks(True)

        layout_text.addWidget(lbl_dev_name)
        layout_text.addWidget(lbl_dev_title)
        layout_text.addWidget(lbl_links)
        layout_text.addStretch()

        layout_dev.addWidget(lbl_photo)
        layout_dev.addSpacing(15)
        layout_dev.addLayout(layout_text)
        
        main_layout.addWidget(group_dev)

        # Tombol Tutup
        btn_close = QPushButton("Tutup")
        btn_close.clicked.connect(self.accept)
        
        layout_tombol = QHBoxLayout()
        layout_tombol.addStretch()
        layout_tombol.addWidget(btn_close)
        
        main_layout.addLayout(layout_tombol)