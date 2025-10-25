# view_widget.py
# Berisi kelas QWidget untuk menampilkan data dalam tabel

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
import db_manager # Impor db_manager untuk memuat data

class ViewWidget(QWidget):
    """Widget untuk menampilkan data dalam tabel."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setStyleSheet("background-color: #008CBA; color: white; padding: 8px; border-radius: 4px;")
        self.refresh_btn.clicked.connect(self.load_data)
        
        layout.addWidget(self.refresh_btn)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def load_data(self):
        """Mengambil data dari db_manager dan menampilkannya di tabel."""
        
        success, data, headers = db_manager.load_data()
        
        if success:
            if not data:
                print("Tidak ada data untuk ditampilkan.")
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(len(headers))
                self.table_widget.setHorizontalHeaderLabels(headers)
                return

            self.table_widget.setColumnCount(len(headers))
            self.table_widget.setHorizontalHeaderLabels(headers)
            self.table_widget.setRowCount(len(data))
            
            for row_idx, row_data in enumerate(data):
                # row_data adalah sqlite3.Row, bisa diakses by index
                for col_idx, col_value in enumerate(row_data):
                    item = QTableWidgetItem(str(col_value))
                    self.table_widget.setItem(row_idx, col_idx, item)
            
            # Sesuaikan lebar kolom 'Alamat' dan 'Keterangan' agar lebih lebar
            try:
                alamat_col = headers.index("Alamat")
                self.table_widget.horizontalHeader().setSectionResizeMode(alamat_col, QHeaderView.ResizeMode.Stretch)
                ket_col = headers.index("Keterangan")
                self.table_widget.horizontalHeader().setSectionResizeMode(ket_col, QHeaderView.ResizeMode.Stretch)
            except ValueError:
                pass # Jika kolom tidak ditemukan

        else:
            # Jika gagal, 'data' berisi pesan error
            QMessageBox.critical(self, "Error", data)