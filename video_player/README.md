# Video Player with TTS

Video player dengan fitur Text-to-Speech untuk subtitle. Mendukung konversi SRT ke audio dengan pilihan suara pria/wanita.

## Fitur

- Pemutaran video dengan VLC backend
- Konversi subtitle (SRT) ke audio menggunakan Edge TTS
- Pilihan suara pria/wanita
- Sinkronisasi audio TTS dengan video
- Playlist manager
- Toggle antara audio asli dan TTS
- Progress bar dan kontrol playback

## Prerequisite

1. Python 3.8+
2. VLC Media Player
3. Dependencies Python:
   ```bash
   pip install PyQt6 python-vlc edge-tts pysrt pydub
   ```

## Penggunaan

1. Jalankan aplikasi:
   ```bash
   python main.py
   ```

2. Menambah video:
   - Klik "Add Video"
   - Pilih file video
   - Pilih file SRT yang sesuai
   - Pilih jenis suara (pria/wanita)

3. Kontrol playback:
   - Play/Pause: Tombol "Play/Pause"
   - Previous/Next: Tombol "Previous"/"Next"
   - Toggle Audio: Switch antara audio asli dan TTS

4. Playlist:
   - Pilih video dari daftar playlist
   - Hapus video dengan tombol "Remove"
   - Playlist akan disimpan otomatis

## Fitur TTS

- Konversi otomatis SRT ke audio saat pertama kali dibutuhkan
- Timing audio sesuai dengan subtitle
- Cache audio TTS untuk penggunaan berikutnya
- Penyesuaian kecepatan bicara otomatis

## Project Structure

```
video_player/
├── core/
│   ├── audio_player.py   # Audio player dan sinkronisasi
│   ├── converter.py      # Konversi TTS
│   └── playlist.py       # Manajemen playlist
├── ui/
│   └── main_window.py    # Interface utama
└── main.py              # Entry point
