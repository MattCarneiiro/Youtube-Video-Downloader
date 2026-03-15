# 🎵 NanoDrop

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/PyQt6-v6.6.1-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Platform">
</div>

---

**NanoDrop** is an elegant, open-source, Apple-inspired desktop application designed to download music and videos from YouTube and YouTube Music. It is highly optimized for portable media players, especially the **Apple iPod** lineup (Nano, Classic, Touch).

Developed with ❤️ by **MattCarneiiroo**.

## ✨ Key Features

- **🎧 Premium Audio for iPods:** Download tracks in **MP3 (320kbps)** or **FLAC (Lossless)**, fully ready to be synced via iTunes or Apple Music.
- **📺 Retro Video Format:** Optimized specifically for older iPods (Nano, Classic). Uses **H.264 Baseline** (max 480p) to bypass iTunes transfer blocks.
- **🏷️ Automatic Metadata (ID3 Tags):** Injects album covers (thumbnails), artist names, and track titles directly into the files. No more messy libraries!
- **📜 Smart Playlist Support:** Paste a YouTube Music album link to download and sequentially number all tracks (e.g., `01 - Song.mp3`).
- **🌓 Sleek UI:** Built with **PyQt6**, featuring a smooth and instant transition between Light and Dark modes.

## 🚀 How to Install and Run

### Prerequisites
Make sure you have [Python 3](https://www.python.org/downloads/) and [FFmpeg](https://ffmpeg.org/download.html) (optional, but recommended) installed.

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MattCarneiiro/Youtube-Video-Downloader.git
   cd Youtube-Video-Downloader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## 🛠️ Technologies Used

- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/):** For the modern, fluid, and responsive graphical interface.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** The powerful core engine for media extraction.
- **[imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg):** For offline post-processing, audio conversion, and thumbnail embedding.

## 📝 Disclaimer & License

This project is intended strictly for **personal and educational use**. Please respect the copyright of the media you download and support the artists.

Distributed under the MIT License. See `LICENSE` for more information (if applicable).

---
<div align="center">
  <sub>Built with python and passion for the NanoDrop project.</sub>
</div>
