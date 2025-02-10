# Pola Sistem

## Arsitektur
- Model-View-Controller (MVC)
  - Models: PlayerModel, TTSModel, VideoModel, PlaylistModel
  - Views: PlayerView, ModernPlayerWindow, PlaylistView
  - Controllers: PlayerController, PlaylistController

## Pola Desain Utama
1. Observer Pattern
   - Untuk sinkronisasi antara video dan TTS
   - Update status pemutaran
   - Notifikasi perubahan playlist

2. Factory Pattern
   - Pembuatan objek video dan TTS
   - Pengelolaan resource

3. Singleton Pattern
   - Manajemen instance player
   - Kontrol TTS
   - Manajemen playlist

## Hubungan Komponen
```
PlayerController
├─ PlayerModel
│  ├─ VideoModel
│  ├─ PlaylistModel
│  └─ TTSModel
└─ PlayerView
   ├─ ModernPlayerWindow
   └─ PlaylistView
```

## Alur Data
1. Input: 
   - File video dan SRT
   - Playlist manual (daftar video)
2. Proses: 
   - Video stream → VideoModel
   - SRT parsing → TTSModel
   - Playlist management → PlaylistModel
3. Output:
   - Video rendering di PlayerView
   - Audio TTS melalui sistem suara
   - Tampilan playlist di PlaylistView