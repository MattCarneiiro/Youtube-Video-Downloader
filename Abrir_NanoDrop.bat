@echo off
title Iniciando NanoDrop...
color 0A

echo =========================================
echo       BEM VINDO AO NANODROP
echo =========================================
echo Verificando e instalando componentes...
pip install pyinstaller PyQt6 yt-dlp imageio-ffmpeg --quiet

echo.
echo Tudo pronto! Abrindo a interface...
python main.py

exit