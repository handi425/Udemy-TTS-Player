import vlc
from dataclasses import dataclass
from typing import Optional, List
from .tts_model import TTSSegment

@dataclass
class PlayerState:
    is_playing: bool = False
    current_time: int = 0  # milliseconds
    duration: int = 0      # milliseconds
    volume: int = 100
    is_using_tts: bool = False
    tts_volume: int = 100

class PlayerModel:
    def __init__(self):
        self._observers = []
        self._instance = vlc.Instance()
        self._video_player = self._instance.media_player_new()
        self._audio_player = self._instance.media_player_new()
        self._state = PlayerState()
        self._current_segments: List[TTSSegment] = []
        self._current_segment_index: int = -1

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, event_type="update", data=None):
        for observer in self._observers:
            observer.on_player_update(event_type, data)

    @property
    def state(self) -> PlayerState:
        return self._state

    def load_video(self, video_path: str, hwnd) -> bool:
        """Load video file"""
        try:
            media = self._instance.media_new(video_path)
            self._video_player.set_media(media)
            self._video_player.set_hwnd(hwnd)  # Set video window
            self._state.current_time = 0
            self.notify_observers("video_loaded")
            return True
        except Exception as e:
            self.notify_observers("error", str(e))
            return False

    def load_tts_segments(self, segments: List[TTSSegment]):
        """Load TTS segments"""
        self._current_segments = segments
        self._current_segment_index = -1
        self.notify_observers("tts_loaded")

    def play(self):
        """Start playback"""
        if not self._state.is_playing:
            self._video_player.play()
            self._state.is_playing = True
            self.notify_observers("playback_started")

    def pause(self):
        """Pause playback"""
        if self._state.is_playing:
            self._video_player.pause()
            if self._state.is_using_tts:
                self._audio_player.pause()
            self._state.is_playing = False
            self.notify_observers("playback_paused")

    def stop(self):
        """Stop playback"""
        self._video_player.stop()
        if self._state.is_using_tts:
            self._audio_player.stop()
        self._state.is_playing = False
        self._state.current_time = 0
        self.notify_observers("playback_stopped")

    def seek(self, position: float):
        """Seek to position (0-1)"""
        self._video_player.set_position(position)
        self._sync_tts_with_video()
        self.notify_observers("position_changed")

    def set_volume(self, volume: int):
        """Set volume (0-100)"""
        if 0 <= volume <= 100:
            if self._state.is_using_tts:
                self._state.tts_volume = volume
                self._audio_player.audio_set_volume(volume)
            else:
                self._state.volume = volume
                self._video_player.audio_set_volume(volume)
            self.notify_observers("volume_changed")

    def toggle_tts(self, enabled: bool):
        """Toggle TTS audio"""
        self._state.is_using_tts = enabled
        if enabled:
            self._video_player.audio_set_volume(0)
            self._audio_player.audio_set_volume(self._state.tts_volume)
        else:
            self._video_player.audio_set_volume(self._state.volume)
            self._audio_player.stop()
        self.notify_observers("tts_toggled")

    def _sync_tts_with_video(self):
        """Sync TTS audio with video position"""
        if not self._state.is_using_tts or not self._current_segments:
            return

        current_time = self._video_player.get_time()
        self._state.current_time = current_time

        # Find appropriate segment
        for i, segment in enumerate(self._current_segments):
            if segment.start_time <= current_time < segment.end_time:
                if i != self._current_segment_index:
                    self._current_segment_index = i
                    # Load and play segment
                    media = self._instance.media_new(segment.file_path)
                    self._audio_player.set_media(media)
                    self._audio_player.play()
                return

        # Stop audio if no matching segment
        if self._audio_player.is_playing():
            self._audio_player.stop()
            self._current_segment_index = -1

    def update(self):
        """Update player state"""
        if self._state.is_playing:
            self._state.current_time = self._video_player.get_time()
            self._state.duration = self._video_player.get_length()
            self._sync_tts_with_video()
            self.notify_observers("time_updated")
