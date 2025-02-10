import asyncio
from typing import Optional
from ..models.video_model import VideoModel
from ..models.tts_model import TTSModel
from ..models.player_model import PlayerModel

class PlayerController:
    def __init__(self, video_model: VideoModel, tts_model: TTSModel, player_model: PlayerModel):
        self.video_model = video_model
        self.tts_model = tts_model
        self.player_model = player_model
        self._preparing_tts = False

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

    def toggle_tts(self, enabled: bool):
        """Toggle TTS audio"""
        video = self.video_model.current_video
        if video and video.is_tts_ready:
            self.player_model.toggle_tts(enabled)

    async def next_video(self, hwnd):
        """Play next video"""
        self.video_model.next_video()
        if self.video_model.current_video:
            await self.play_video(hwnd)

    async def previous_video(self, hwnd):
        """Play previous video"""
        self.video_model.previous_video()
        if self.video_model.current_video:
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
