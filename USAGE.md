# Video Player with TTS - Panduan Penggunaan

## Fitur Utama
1. Pemutaran video dengan subtitle
2. Konversi otomatis subtitle ke audio (Text-to-Speech)
3. Pilihan suara pria/wanita untuk TTS
4. Sinkronisasi timing audio TTS dengan video
5. Playlist manager untuk multiple video
6. Volume control terpisah untuk audio asli dan TTS
7. Cache system untuk audio TTS

## Cara Penggunaan

### 1. Memulai Aplikasi
```bash
python video_player/main.py
```

### 2. Menambah Video
1. Klik tombol "Add Video"
2. Pilih file video (.mp4, .avi, .mkv)
3. Pilih file subtitle (.srt)
4. Video akan ditambahkan ke playlist

### 3. Kontrol Video
- Play/Pause: Tombol "Play/Pause"
- Previous/Next: Tombol navigasi
- Progress Bar: Drag untuk pindah posisi video
- Volume: Gunakan slider volume

### 4. Fitur TTS
1. Pilih jenis suara (pria/wanita) di dropdown
2. Klik "Toggle Audio" untuk beralih antara audio asli dan TTS
3. TTS akan digenerate otomatis saat pertama kali digunakan
4. Audio TTS akan di-cache untuk penggunaan berikutnya

### 5. Playlist Management
- Tambah video baru: "Add Video"
- Hapus video: Pilih video dan klik "Remove"
- Playlist disimpan otomatis
- Load playlist otomatis saat aplikasi dibuka

## Tips Penggunaan
1. Pastikan subtitle (.srt) sesuai dengan timing video
2. Gunakan volume control untuk menyesuaikan level audio TTS
3. TTS akan otomatis sync dengan video sesuai timing subtitle
4. Fade effect akan aktif saat switching audio

## Troubleshooting
1. Jika audio TTS tidak terdengar:
   - Cek volume slider
   - Pastikan subtitle file valid
   - Coba generate ulang TTS

2. Jika video tidak muncul:
   - Pastikan format video didukung
   - Cek codec video

3. Masalah timing:
   - Pastikan subtitle timing sesuai
   - Coba load ulang video

## System Requirements
- Python 3.8+
- VLC Media Player
- Dependencies (auto-install):
  - PyQt6
  - python-vlc
  - edge-tts
  - pysrt
  - pydub
