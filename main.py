# main.py
# File utama untuk menjalankan aplikasi

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget
)
from PyQt6.QtGui import QAction, QFont

# Impor file-file (widget dan db manager) yang sudah kita buat
import db_manager
from form_widget import FormWidget
from view_widget import ViewWidget

class MainWindow(QMainWindow):
    """Jendela utama aplikasi yang berisi menu dan stacked widget."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Aplikasi Pendaftaran NPWP')
        self.setGeometry(100, 100, 800, 700) # Perbesar sedikit

        self.setup_menu()
        self.setup_main_widgets()
        
        self.show_form_page() # Tampilkan halaman form saat pertama kali dibuka

    def setup_menu(self):
        """Membuat dan mengatur Menu Bar."""
        menu_bar = self.menuBar()
        
        # Menu "File"
        file_menu = menu_bar.addMenu('File')
        
        exit_action = QAction('Keluar', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu "Navigasi"
        nav_menu = menu_bar.addMenu('Navigasi')
        
        add_data_action = QAction('Tambah Data Pendaftaran', self)
        add_data_action.triggered.connect(self.show_form_page)
        nav_menu.addAction(add_data_action)
        
        view_data_action = QAction('Lihat Data Pendaftaran', self)
        view_data_action.triggered.connect(self.show_view_page)
        nav_menu.addAction(view_data_action)

    def setup_main_widgets(self):
        """Membuat QStackedWidget dan menambahkan halaman-halaman."""
        
        # --- Setup QStackedWidget ---
        self.stacked_widget = QStackedWidget()
        
        # Buat instance dari kedua widget halaman
        self.form_page = FormWidget()
        self.view_page = ViewWidget()
        
        # Tambahkan halaman ke stacked widget
        self.stacked_widget.addWidget(self.form_page)
        self.stacked_widget.addWidget(self.view_page)

        # Set widget utama dari QMainWindow
        self.setCentralWidget(self.stacked_widget)

        # --- Hubungkan Sinyal ---
        # Saat form_page mengirim sinyal 'data_saved', panggil self.refresh_tabel_data
        self.form_page.data_saved.connect(self.refresh_tabel_data)

    def show_form_page(self):
        """Beralih ke tampilan formulir."""
        self.stacked_widget.setCurrentWidget(self.form_page)
        self.setWindowTitle('Aplikasi Pendaftaran NPWP - Tambah Data')

    def show_view_page(self):
        """Beralih ke tampilan tabel dan me-refresh datanya."""
        self.view_page.load_data() # Selalu refresh saat halaman dibuka
        self.stacked_widget.setCurrentWidget(self.view_page)
        self.setWindowTitle('Aplikasi Pendaftaran NPWP - Lihat Data')
        
    def refresh_tabel_data(self):
        """
        Slot yang dipanggil oleh sinyal 'data_saved' dari FormWidget.
        Ini me-refresh data di tabel *bahkan jika* tabel sedang tidak terlihat.
        """
        print("Sinyal diterima, me-refresh data tabel...")
        self.view_page.load_data()


# --- Main execution ---
if __name__ == '__main__':
    # Inisialisasi DB sekali di awal
    db_manager.init_db() 
    
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion") 
    
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())