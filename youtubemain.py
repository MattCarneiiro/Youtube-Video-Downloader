import sys
import os
import yt_dlp
import imageio_ffmpeg
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QProgressBar,
                             QFileDialog, QMessageBox, QComboBox, QRadioButton, 
                             QButtonGroup, QSpacerItem, QSizePolicy, QCheckBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class WorkerProcess(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str) 
    error = pyqtSignal(str)
    
    def __init__(self, url, folder, format_choice, embed_metadata):
        super().__init__()
        self.url = url
        self.folder = folder
        self.format_choice = format_choice
        self.embed_metadata = embed_metadata # Nova variável que recebe se a caixa está marcada

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = int((downloaded / total) * 100)
                self.progress.emit(percent)
        elif d['status'] == 'finished':
            # Como o ffmpeg processa a capa e o áudio depois do download, deixamos em 99% 
            # até que tudo realmente termine.
            self.progress.emit(99)

    def run(self):
        try:
            out_path = os.path.join(self.folder, '%(title)s.%(ext)s')
            
            opts = {
                'outtmpl': out_path,
                'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'noprogress': True,
                'postprocessors': [] # Inicializamos a lista vazia para adicionar coisas depois
            }

            # 1. Configuração de Vídeo ou Áudio
            if self.format_choice == "windows":
                opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                opts['merge_output_format'] = 'mp4'
                
            elif self.format_choice == "max":
                opts['format'] = 'bestvideo+bestaudio/best'
                opts['merge_output_format'] = 'mkv'
                
            elif self.format_choice == "audio_flac":
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'].append({
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                })
                
            elif self.format_choice == "audio_mp3":
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'].append({
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                })

            # 2. Configuração de Metadados (A Mágica da Capinha)
            if self.embed_metadata:
                opts['writethumbnail'] = True # Manda baixar a capa
                
                # Injeta as informações de texto (Artista, Álbum, etc)
                opts['postprocessors'].append({'key': 'FFmpegMetadata'})
                
                # Injeta a imagem da capa dentro do arquivo (O iPod ama isso)
                opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                })

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
                
            self.progress.emit(100)
            self.finished.emit("Download concluído! A mídia já está pronta para o seu iPod.")
        except Exception as e:
            self.error.emit(str(e))

class AppDownloadEducacional(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = True 
        self.initUI()
        self.apply_theme()
        
    def initUI(self):
        self.setWindowTitle("Baixador Mídia (iPod Edition)")
        self.setFixedSize(520, 520) # Aumentei um pouquinho para caber a nova caixa
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # --- Top Bar ---
        top_layout = QHBoxLayout()
        self.label_title = QLabel("Baixador de Mídia")
        self.label_title.setStyleSheet("font-size: 22px; font-weight: 800; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;")
        
        self.btn_theme = QPushButton("☀️ Mudar Tema")
        self.btn_theme.setObjectName("btn_theme")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)
        
        top_layout.addWidget(self.label_title)
        top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        top_layout.addWidget(self.btn_theme)
        layout.addLayout(top_layout)
        
        # --- Entradas ---
        self.label_url = QLabel("URL do Vídeo (YouTube):")
        self.label_url.setStyleSheet("font-weight: 600; font-size: 13px;")
        
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Cole o link aqui...")
        self.input_url.setMinimumHeight(40)
        
        layout.addWidget(self.label_url)
        layout.addWidget(self.input_url)
        
        self.label_folder = QLabel("Salvar em:")
        self.label_folder.setStyleSheet("font-weight: 600; font-size: 13px;")
        
        folder_layout = QHBoxLayout()
        self.input_folder = QLineEdit()
        self.input_folder.setReadOnly(True)
        self.input_folder.setMinimumHeight(40)
        
        self.btn_browse = QPushButton("Procurar")
        self.btn_browse.setObjectName("btn_browse")
        self.btn_browse.setMinimumHeight(40)
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.input_folder)
        folder_layout.addWidget(self.btn_browse)
        
        layout.addWidget(self.label_folder)
        layout.addLayout(folder_layout)
        
        # --- Seleção Vídeo/Áudio ---
        tipo_layout = QHBoxLayout()
        self.radio_video = QRadioButton("Vídeo (MP4/MKV)")
        self.radio_audio = QRadioButton("Somente Áudio")
        self.radio_video.setChecked(True)
        
        self.grupo_tipo = QButtonGroup()
        self.grupo_tipo.addButton(self.radio_video)
        self.grupo_tipo.addButton(self.radio_audio)
        
        self.radio_video.toggled.connect(self.atualizar_opcoes_formato)
        self.radio_audio.toggled.connect(self.atualizar_opcoes_formato)
        
        tipo_layout.addWidget(self.radio_video)
        tipo_layout.addWidget(self.radio_audio)
        layout.addLayout(tipo_layout)
        
        # --- Qualidade ---
        self.combo_format = QComboBox()
        self.combo_format.setMinimumHeight(40)
        self.atualizar_opcoes_formato()
        layout.addWidget(self.combo_format)
        
        # --- NOVIDADE: Checkbox de Metadados ---
        self.check_metadata = QCheckBox("Embutir Capa e Metadados (Ideal para iPod)")
        self.check_metadata.setChecked(True) # Já deixamos marcado por padrão pra você!
        self.check_metadata.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.check_metadata)
        
        # --- Progresso ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(20)
        layout.addWidget(self.progress_bar)
        
        # --- Botão Baixar ---
        self.btn_download = QPushButton("Iniciar Download")
        self.btn_download.setObjectName("btn_download")
        self.btn_download.setMinimumHeight(50)
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.clicked.connect(self.start_download)
        layout.addWidget(self.btn_download)
        
        self.setLayout(layout)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_mode:
            self.btn_theme.setText("☀️ Modo Claro")
            style = """
                QWidget { background-color: #1C1C1E; color: #F2F2F7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
                
                QLineEdit, QComboBox { background-color: #2C2C2E; border: 1px solid #3A3A3C; border-radius: 8px; padding: 8px 12px; color: #FFFFFF; font-size: 13px; }
                QLineEdit:focus, QComboBox:focus { border: 2px solid #0A84FF; }
                
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { background-color: #2C2C2E; color: #FFFFFF; selection-background-color: #0A84FF; border-radius: 8px; outline: none; }
                
                QPushButton#btn_download { background-color: #0A84FF; color: white; font-weight: bold; font-size: 15px; border-radius: 10px; border: none; }
                QPushButton#btn_download:hover { background-color: #0070E0; }
                QPushButton#btn_download:disabled { background-color: #3A3A3C; color: #8E8E93; }
                
                QPushButton#btn_browse { background-color: #3A3A3C; color: white; border-radius: 8px; padding: 0 15px; border: none; font-weight: 600; }
                QPushButton#btn_browse:hover { background-color: #48484A; }
                
                QPushButton#btn_theme { background-color: transparent; border: 1px solid #3A3A3C; color: #F2F2F7; border-radius: 15px; padding: 5px 15px; font-weight: 600; }
                QPushButton#btn_theme:hover { background-color: #2C2C2E; }
                
                QProgressBar { border: none; background-color: #2C2C2E; border-radius: 10px; text-align: center; color: white; font-weight: bold;}
                QProgressBar::chunk { background-color: #34C759; border-radius: 10px; }
                
                QRadioButton, QCheckBox { font-weight: 600; font-size: 13px; }
            """
        else:
            self.btn_theme.setText("🌙 Modo Escuro")
            style = """
                QWidget { background-color: #F2F2F7; color: #1C1C1E; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
                
                QLineEdit, QComboBox { background-color: #FFFFFF; border: 1px solid #D1D1D6; border-radius: 8px; padding: 8px 12px; color: #000000; font-size: 13px; }
                QLineEdit:focus, QComboBox:focus { border: 2px solid #007AFF; }
                
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { background-color: #FFFFFF; color: #000000; selection-background-color: #007AFF; border-radius: 8px; outline: none; }
                
                QPushButton#btn_download { background-color: #007AFF; color: white; font-weight: bold; font-size: 15px; border-radius: 10px; border: none; }
                QPushButton#btn_download:hover { background-color: #005BB5; }
                QPushButton#btn_download:disabled { background-color: #D1D1D6; color: #8E8E93; }
                
                QPushButton#btn_browse { background-color: #E5E5EA; color: black; border-radius: 8px; padding: 0 15px; border: none; font-weight: 600; }
                QPushButton#btn_browse:hover { background-color: #D1D1D6; }
                
                QPushButton#btn_theme { background-color: transparent; border: 1px solid #D1D1D6; color: #1C1C1E; border-radius: 15px; padding: 5px 15px; font-weight: 600; }
                QPushButton#btn_theme:hover { background-color: #E5E5EA; }
                
                QProgressBar { border: none; background-color: #E5E5EA; border-radius: 10px; text-align: center; color: black; font-weight: bold;}
                QProgressBar::chunk { background-color: #34C759; border-radius: 10px; }
                
                QRadioButton, QCheckBox { font-weight: 600; font-size: 13px; }
            """
        self.setStyleSheet(style)
        
    def atualizar_opcoes_formato(self):
        self.combo_format.clear()
        if self.radio_video.isChecked():
            self.combo_format.addItem("Compatível com Windows/Apple (MP4 / H.264)", "windows")
            self.combo_format.addItem("Altíssima Qualidade (MKV)", "max")
        else:
            self.combo_format.addItem("Áudio Excelente (MP3 - 320kbps - Perfeito p/ iPod)", "audio_mp3")
            self.combo_format.addItem("Áudio Primoroso (FLAC - Formato sem perdas)", "audio_flac")
            
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino")
        if folder:
            self.input_folder.setText(folder)
            
    def start_download(self):
        url = self.input_url.text().strip()
        folder = self.input_folder.text().strip()
        format_choice = self.combo_format.currentData()
        
        # Pega o estado da caixinha (True ou False)
        embed_metadata = self.check_metadata.isChecked()
        
        if not url:
            QMessageBox.warning(self, "Aviso", "Por favor, insira a URL do vídeo.")
            return
        if not folder:
            QMessageBox.warning(self, "Aviso", "Por favor, escolha a pasta de destino.")
            return
            
        self.btn_download.setEnabled(False)
        self.btn_download.setText("Baixando e Processando...")
        self.progress_bar.setValue(0)
        
        # Passamos a nova variável para o trabalhador
        self.worker = WorkerProcess(url, folder, format_choice, embed_metadata)
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
        self.btn_download.setText("Iniciar Download")
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AppDownloadEducacional()
    window.show()
    sys.exit(app.exec())