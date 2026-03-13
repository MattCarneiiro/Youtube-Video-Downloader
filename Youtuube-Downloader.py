import sys
import os
import yt_dlp
import imageio_ffmpeg
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QProgressBar,
                             QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class WorkerProcess(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str) # Success message 
    error = pyqtSignal(str)
    
    def __init__(self, url, folder, format_choice):
        super().__init__()
        self.url = url
        self.folder = folder
        self.format_choice = format_choice

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = int((downloaded / total) * 100)
                self.progress.emit(percent)
        elif d['status'] == 'finished':
            self.progress.emit(100)

    def run(self):
        try:
            out_path = os.path.join(self.folder, '%(title)s.%(ext)s')
            
            opts = {
                'outtmpl': out_path,
                'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'noprogress': True
            }

            if self.format_choice == "windows":
                # Windows (MP4 Compatível): Puxa o melhor vídeo H.264 e melhor M4A, garantindo reprodução nativa
                opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                opts['merge_output_format'] = 'mp4'
            else:
                # Máxima do YouTube Absoluta: Pode baixar AV1/VP9 (4K/8K reais) e juntar num contêiner MKV pra não perder dados
                opts['format'] = 'bestvideo+bestaudio/best'
                opts['merge_output_format'] = 'mkv'
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
            self.finished.emit("Vídeo baixado com sucesso na pasta selecionada!")
        except Exception as e:
            self.error.emit(str(e))

class AppDownloadEducacional(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Baixador Didático (PyQt6)")
        self.setFixedSize(500, 390)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # URL Label
        self.label_url = QLabel("URL do Vídeo (YouTube):")
        self.label_url.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        # URL Input
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Cole o link aqui...")
        self.input_url.setMinimumHeight(35)
        self.input_url.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        
        layout.addWidget(self.label_url)
        layout.addWidget(self.input_url)
        
        # Folder Focus
        self.label_folder = QLabel("Salvar em:")
        self.label_folder.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        folder_layout = QHBoxLayout()
        self.input_folder = QLineEdit()
        self.input_folder.setReadOnly(True)
        self.input_folder.setMinimumHeight(35)
        self.input_folder.setStyleSheet("""
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f7f7f7;
                font-size: 13px;
            }
        """)
        
        self.btn_browse = QPushButton("Procurar...")
        self.btn_browse.setMinimumHeight(35)
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self.btn_browse.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.input_folder)
        folder_layout.addWidget(self.btn_browse)
        
        layout.addWidget(self.label_folder)
        layout.addLayout(folder_layout)
        
        # Format Selection
        self.label_format = QLabel("Qualidade e Formato:")
        self.label_format.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.combo_format = QComboBox()
        self.combo_format.addItem("Altíssima Qualidade (Melhor possível, requer player como VLC)", "max")
        self.combo_format.addItem("Compatível com Windows (MP4 / H.264)", "windows")
        self.combo_format.setCurrentIndex(1) # Default to Windows compatible
        self.combo_format.setMinimumHeight(35)
        self.combo_format.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border-left: 1px solid #ccc;
                width: 30px;
            }
        """)
        
        layout.addWidget(self.label_format)
        layout.addWidget(self.combo_format)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Download Button
        self.btn_download = QPushButton("Baixar Vídeo")
        self.btn_download.setMinimumHeight(45)
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_download.clicked.connect(self.start_download)
        
        layout.addWidget(self.btn_download)
        self.setLayout(layout)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino")
        if folder:
            self.input_folder.setText(folder)
            
    def start_download(self):
        url = self.input_url.text().strip()
        folder = self.input_folder.text().strip()
        format_choice = self.combo_format.currentData()
        
        if not url:
            QMessageBox.warning(self, "Aviso", "Por favor, insira a URL do vídeo.")
            return
        if not folder:
            QMessageBox.warning(self, "Aviso", "Por favor, escolha a pasta de destino.")
            return
            
        self.btn_download.setEnabled(False)
        self.btn_download.setText("Baixando... Aguarde")
        self.progress_bar.setValue(0)
        
        # Create user thread
        self.worker = WorkerProcess(url, folder, format_choice)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.download_error)
        self.worker.start()
        
    def update_progress(self, percent):
        self.progress_bar.setValue(percent)
        
    def download_finished(self, msg):
        self.reset_ui()
        QMessageBox.information(self, "Sucesso", msg)
        
    def download_error(self, err_msg):
        self.reset_ui()
        QMessageBox.critical(self, "Erro", f"Ops, ocorreu um erro ao baixar:\n{err_msg}")
        
    def reset_ui(self):
        self.btn_download.setEnabled(True)
        self.btn_download.setText("Baixar Vídeo")
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern bright style fallback
    app.setStyle("Fusion")
    
    window = AppDownloadEducacional()
    window.show()
    sys.exit(app.exec())