import sys
import os
import yt_dlp
import imageio_ffmpeg
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QProgressBar,
                             QFileDialog, QMessageBox, QComboBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class WorkerProcess(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str) 
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

            # Lógica para as novas escolhas
            if self.format_choice == "windows":
                opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                opts['merge_output_format'] = 'mp4'
                
            elif self.format_choice == "max":
                opts['format'] = 'bestvideo+bestaudio/best'
                opts['merge_output_format'] = 'mkv'
                
            elif self.format_choice == "audio_flac":
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                }]
                
            elif self.format_choice == "audio_mp3":
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }]

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
                
            self.finished.emit("Download concluído com sucesso na pasta selecionada!")
        except Exception as e:
            self.error.emit(str(e))

class AppDownloadEducacional(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Baixador Didático Avançado (PyQt6)")
        self.setFixedSize(500, 450) # Aumentei um pouco a altura para caber os botões
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # URL Label e Input
        self.label_url = QLabel("URL do Vídeo (YouTube):")
        self.label_url.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Cole o link aqui...")
        self.input_url.setMinimumHeight(35)
        self.input_url.setStyleSheet("""
            QLineEdit { padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #4CAF50; }
        """)
        
        layout.addWidget(self.label_url)
        layout.addWidget(self.input_url)
        
        # Pasta de Destino
        self.label_folder = QLabel("Salvar em:")
        self.label_folder.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        folder_layout = QHBoxLayout()
        self.input_folder = QLineEdit()
        self.input_folder.setReadOnly(True)
        self.input_folder.setMinimumHeight(35)
        self.input_folder.setStyleSheet("QLineEdit { padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; background-color: #f7f7f7; font-size: 13px; }")
        
        self.btn_browse = QPushButton("Procurar...")
        self.btn_browse.setMinimumHeight(35)
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.input_folder)
        folder_layout.addWidget(self.btn_browse)
        
        layout.addWidget(self.label_folder)
        layout.addLayout(folder_layout)
        
        # --- NOVIDADE: Seleção de Tipo (Vídeo ou Áudio) ---
        tipo_layout = QHBoxLayout()
        self.radio_video = QRadioButton("Baixar Vídeo (com áudio)")
        self.radio_audio = QRadioButton("Baixar Somente Áudio")
        self.radio_video.setChecked(True) # O padrão é vídeo
        
        # Agrupando para que apenas um possa ser clicado por vez
        self.grupo_tipo = QButtonGroup()
        self.grupo_tipo.addButton(self.radio_video)
        self.grupo_tipo.addButton(self.radio_audio)
        
        # Conectando os botões para atualizar a lista de qualidade
        self.radio_video.toggled.connect(self.atualizar_opcoes_formato)
        self.radio_audio.toggled.connect(self.atualizar_opcoes_formato)
        
        tipo_layout.addWidget(self.radio_video)
        tipo_layout.addWidget(self.radio_audio)
        layout.addLayout(tipo_layout)
        # ----------------------------------------------------
        
        # Seleção de Formato / Qualidade
        self.label_format = QLabel("Qualidade e Formato:")
        self.label_format.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.combo_format = QComboBox()
        self.combo_format.setMinimumHeight(35)
        self.combo_format.setStyleSheet("QComboBox { padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; background-color: white; font-size: 13px; }")
        
        layout.addWidget(self.label_format)
        layout.addWidget(self.combo_format)
        
        # Preenche o combo box inicial (Vídeo)
        self.atualizar_opcoes_formato()
        
        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #ccc; border-radius: 4px; text-align: center; }
            QProgressBar::chunk { background-color: #4CAF50; width: 10px; }
        """)
        layout.addWidget(self.progress_bar)
        
        # Botão Baixar
        self.btn_download = QPushButton("Baixar Mídia")
        self.btn_download.setMinimumHeight(45)
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """)
        self.btn_download.clicked.connect(self.start_download)
        
        layout.addWidget(self.btn_download)
        self.setLayout(layout)
        
    def atualizar_opcoes_formato(self):
        """Atualiza a lista do QComboBox dependendo se Vídeo ou Áudio está marcado"""
        self.combo_format.clear()
        
        if self.radio_video.isChecked():
            self.combo_format.addItem("Compatível com Windows (MP4 / H.264)", "windows")
            self.combo_format.addItem("Altíssima Qualidade (Melhor possível, requer VLC)", "max")
        else:
            self.combo_format.addItem("Áudio Primoroso (FLAC - Formato sem perdas)", "audio_flac")
            self.combo_format.addItem("Áudio Excelente (MP3 - 320kbps - Compatível)", "audio_mp3")
            
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
        
        # Cria a thread do trabalhador
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
        self.btn_download.setText("Baixar Mídia")
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AppDownloadEducacional()
    window.show()
    sys.exit(app.exec())