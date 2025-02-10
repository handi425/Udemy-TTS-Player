import asyncio
from typing import Optional
from ..models.video_model import VideoModel
from ..models.tts_model import TTSModel
from ..models.player_model import PlayerModel
from PyQt5.QtCore import QObject, pyqtSignal
import os

class PlayerController(QObject):
    conversion_status = pyqtSignal(str)  # Signal untuk status konversi
    
    def __init__(self, video_model: VideoModel, tts_model: TTSModel, player_model: PlayerModel):
        super().__init__()
        self.video_model = video_model
        self.tts_model = tts_model
        self.player_model = player_model
        self._preparing_tts = False
        self.view = None
        self.loop = asyncio.get_event_loop()

    def setup_view(self, view):
        """Setup view setelah inisialisasi"""
        self.view = view
        self._setup_connections()
        
    def _setup_connections(self):
        """Setup koneksi antara view dan controller"""
        if not self.view:
            return
            
        # Koneksi tombol kontrol video
        self.view.play_button.clicked.connect(self._handle_play)
        self.view.prev_button.clicked.connect(lambda: asyncio.create_task(self.previous_video()))
        self.view.next_button.clicked.connect(lambda: asyncio.create_task(self.next_video()))
        self.view.volume_slider.valueChanged.connect(self.player_model.set_volume)
        
        # Koneksi untuk konversi dan bahasa
        self.view.tts_toggle.clicked.connect(self.toggle_tts)
        self.view.voice_selector.currentTextChanged.connect(self._update_voice_type)
        self.view.source_language.currentIndexChanged.connect(self._update_source_language)
        self.view.target_language.currentIndexChanged.connect(self._update_target_language)
        
        # Koneksi progress konversi
        if hasattr(self.tts_model, 'conversion_progress'):
            self.tts_model.conversion_progress.connect(self.view.update_progress)
        if hasattr(self.tts_model, 'conversion_complete'):
            self.tts_model.conversion_complete.connect(self._on_conversion_complete)
    
    async def prepare_tts(self, video_data) -> bool:
        """Prepare TTS audio before playing video"""
        if self._preparing_tts:
            return False

        self._preparing_tts = True
        try:
            # Generate TTS if not ready
            if not video_data.is_tts_ready:
                tts_dir = f"tts_output/video_{self.video_model.current_index}"
                self.tts_model.set_voice_type(video_data.voice_type)
                segments = await self.tts_model.generate_tts(video_data.srt_path, tts_dir)
                self.video_model.set_tts_ready(self.video_model.current_index, tts_dir)
                self.player_model.load_tts_segments(segments)
            return True
        except Exception as e:
            print(f"Error preparing TTS: {str(e)}")
            return False
        finally:
            self._preparing_tts = False

    async def play_video(self, hwnd) -> bool:
        """Play video with TTS preparation"""
        video = self.video_model.current_video
        if not video:
            return False

        # Prepare TTS first
        if not await self.prepare_tts(video):
            return False

        # Load and play video
        if self.player_model.load_video(video.video_path, hwnd):
            self.player_model.play()
            return True
        return False

    def toggle_playback(self):
        """Toggle play/pause"""
        if self.player_model.state.is_playing:
            self.player_model.pause()
        else:
            self.player_model.play()

    def stop_playback(self):
        """Stop playback"""
        self.player_model.stop()

    def seek_video(self, position: float):
        """Seek to position (0-1)"""
        self.player_model.seek(position)

    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        self.player_model.set_volume(volume)

    def toggle_tts(self, enabled: bool = None):
        """Toggle TTS on/off"""
        if enabled is None:
            enabled = not self.player_model.state.is_using_tts
        self.player_model.toggle_tts(enabled)

    async def next_video(self, hwnd=None):
        """Play next video"""
        self.video_model.next_video()
        if self.video_model.current_video:
            if hwnd is None:
                hwnd = self.view.video_frame.winId()
            await self.play_video(hwnd)

    async def previous_video(self, hwnd=None):
        """Play previous video"""
        self.video_model.previous_video()
        if self.video_model.current_video:
            if hwnd is None:
                hwnd = self.view.video_frame.winId()
            await self.play_video(hwnd)

    def add_video(self, video_path: str, srt_path: str, voice_type: str = "pria"):
        """Add video to playlist"""
        return self.video_model.add_video(video_path, srt_path, voice_type)

    def remove_video(self, index: int):
        """Remove video from playlist"""
        self.video_model.remove_video(index)

    def load_playlist(self, data: dict):
        """Load playlist data"""
        self.video_model.load_from_dict(data)

    def save_playlist(self) -> dict:
        """Save playlist data"""
        return self.video_model.to_dict()

    def _handle_play(self):
        """Menangani klik tombol play dengan proses konversi"""
        if not self.player_model.state.is_playing:
            current_video = self.video_model.current_video
            if current_video and os.path.exists(current_video.video_path):
                srt_path = current_video.srt_path
                if os.path.exists(srt_path):
                    # Mulai proses konversi
                    self.conversion_status.emit("Memulai konversi subtitle...")
                    self.view.show_loading(True)
                    
                    # Generate TTS jika belum siap
                    if not current_video.is_tts_ready:
                        tts_dir = f"tts_output/video_{self.video_model.current_index}"
                        self.tts_model.set_voice_type(current_video.voice_type)
                        success = self.tts_model.convert_srt_to_audio(srt_path, tts_dir)
                        
                        if success:
                            self.video_model.set_tts_ready(self.video_model.current_index, tts_dir)
                            self.conversion_status.emit("Konversi selesai, memulai pemutaran...")
                            self.player_model.play()
                        else:
                            self.conversion_status.emit("Gagal melakukan konversi")
                            self.view.show_loading(False)
                    else:
                        # TTS sudah siap, langsung putar
                        self.player_model.play()
                else:
                    # Jika tidak ada SRT, langsung putar video
                    self.player_model.play()
        else:
            self.player_model.pause()
    
    def _handle_conversion(self):
        """Menangani proses konversi video dengan TTS"""
        current_video = self.player_model.get_current_video()
        if current_video and os.path.exists(current_video):
            srt_path = current_video.replace('.mp4', '.srt')
            if os.path.exists(srt_path):
                # Generate audio TTS
                audio_path = current_video.replace('.mp4', '_tts.mp3')
                success = self.tts_model.convert_srt_to_audio(srt_path, audio_path)
                
                if success:
                    # Merge video dengan audio baru
                    output_path = current_video.replace('.mp4', '_with_tts.mp4')
                    if self.tts_model.merge_video_and_audio(current_video, audio_path, output_path):
                        self.conversion_status.emit("Konversi video berhasil!")
                        # Update playlist dengan video yang baru
                        self.player_model.update_current_video(output_path)
                    else:
                        self.conversion_status.emit("Gagal menggabungkan video dan audio")
                else:
                    self.conversion_status.emit("Gagal mengkonversi subtitle ke audio")
    
    def _update_source_language(self, index):
        """Update bahasa sumber"""
        lang_code = self.view.source_language.itemData(index)
        if lang_code:
            self.tts_model.set_language(lang_code, self.tts_model.current_target_lang)
            # Update model yang tersedia
            available_models = self.tts_model.get_available_models(lang_code)
            self.view.update_source_models(available_models)
    
    def _update_target_language(self, index):
        """Update bahasa target"""
        lang_code = self.view.target_language.itemData(index)
        if lang_code:
            self.tts_model.set_language(self.tts_model.current_source_lang, lang_code)
            # Update model yang tersedia
            available_models = self.tts_model.get_available_models(lang_code)
            self.view.update_target_models(available_models)
    
    def _on_conversion_complete(self):
        """Handler ketika konversi selesai"""
        self.view.show_loading(False)
        self.conversion_status.emit("Konversi selesai")

    def _update_voice_type(self, voice_type: str):
        """Update tipe suara TTS"""
        self.tts_model.set_voice_type("pria" if voice_type == "Male" else "wanita")

    def toggle_tts(self):
        """Toggle TTS on/off"""
        state = self.player_model.state
        self.player_model.toggle_tts(not state.is_using_tts)
