from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class VideoData:
    video_path: str
    srt_path: str
    tts_dir: Optional[str] = None
    voice_type: str = "pria"
    is_tts_ready: bool = False

class VideoModel:
    def __init__(self):
        self._videos: list[VideoData] = []
        self._current_index: int = -1
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.on_model_updated()

    @property
    def current_video(self) -> Optional[VideoData]:
        if 0 <= self._current_index < len(self._videos):
            return self._videos[self._current_index]
        return None

    @property
    def current_index(self) -> int:
        return self._current_index

    def add_video(self, video_path: str, srt_path: str, voice_type: str = "pria") -> VideoData:
        video = VideoData(
            video_path=video_path,
            srt_path=srt_path,
            voice_type=voice_type
        )
        self._videos.append(video)
        self.notify_observers()
        return video

    def remove_video(self, index: int):
        if 0 <= index < len(self._videos):
            video = self._videos.pop(index)
            if video.tts_dir and os.path.exists(video.tts_dir):
                # Cleanup TTS files
                for file in os.listdir(video.tts_dir):
                    os.remove(os.path.join(video.tts_dir, file))
                os.rmdir(video.tts_dir)
            self.notify_observers()

    def set_current(self, index: int):
        if 0 <= index < len(self._videos):
            self._current_index = index
            self.notify_observers()

    def next_video(self):
        if self._current_index < len(self._videos) - 1:
            self._current_index += 1
            self.notify_observers()

    def previous_video(self):
        if self._current_index > 0:
            self._current_index -= 1
            self.notify_observers()

    def set_tts_ready(self, index: int, tts_dir: str):
        if 0 <= index < len(self._videos):
            self._videos[index].tts_dir = tts_dir
            self._videos[index].is_tts_ready = True
            self.notify_observers()

    def to_dict(self):
        return {
            'videos': [
                {
                    'video_path': v.video_path,
                    'srt_path': v.srt_path,
                    'tts_dir': v.tts_dir,
                    'voice_type': v.voice_type,
                    'is_tts_ready': v.is_tts_ready
                }
                for v in self._videos
            ],
            'current_index': self._current_index
        }

    def load_from_dict(self, data: dict):
        self._videos = [
            VideoData(**video_data)
            for video_data in data.get('videos', [])
        ]
        self._current_index = data.get('current_index', -1)
        self.notify_observers()
