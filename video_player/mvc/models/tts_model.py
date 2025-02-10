import asyncio
import edge_tts
import pysrt
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class TTSSegment:
    file_path: str
    start_time: int  # milliseconds
    end_time: int    # milliseconds
    text: str
    rate: str

VOICE_LIST = {
    "pria": "id-ID-ArdiNeural",
    "wanita": "id-ID-GadisNeural"
}

class TTSModel:
    def __init__(self):
        self._observers = []
        self._current_segments: List[TTSSegment] = []
        self._is_generating = False
        self._progress = 0
        self._voice_type = "pria"
        self._global_speed = 1.15

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, event_type="update", data=None):
        for observer in self._observers:
            observer.on_tts_update(event_type, data)

    @property
    def is_generating(self) -> bool:
        return self._is_generating

    @property
    def progress(self) -> int:
        return self._progress

    def set_voice_type(self, voice_type: str):
        if voice_type in VOICE_LIST:
            self._voice_type = voice_type

    def calculate_speech_rate(self, text_length: int, duration_ms: int) -> str:
        """Menghitung rate berdasarkan panjang teks dan durasi"""
        duration_ms = max(duration_ms, 1000)  # Minimal 1 detik
        base_wpm = 100  # Base words per minute
        estimated_words = text_length / 5
        duration_minutes = duration_ms / (1000 * 60)
        target_wpm = (estimated_words / duration_minutes) * self._global_speed
        rate_change = int((target_wpm / base_wpm - 1) * 100)
        rate_change = min(max(rate_change, -30), 150)
        return f"{rate_change:+d}%"

    async def text_to_speech(self, text: str, output_file: str, rate: str):
        """Mengkonversi teks ke audio"""
        communicate = edge_tts.Communicate(
            text, 
            VOICE_LIST[self._voice_type], 
            rate=rate
        )
        await communicate.save(output_file)

    async def generate_tts(self, srt_path: str, output_dir: str) -> List[TTSSegment]:
        """Generate TTS untuk file SRT"""
        self._is_generating = True
        self._progress = 0
        self.notify_observers("generation_started")

        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            subs = pysrt.open(srt_path)
            total_subs = len(subs)
            segments = []

            for i, sub in enumerate(subs):
                output_file = os.path.join(output_dir, f"segment_{i+1}.mp3")
                
                # Calculate timing
                start_time = (sub.start.hours * 3600000 + 
                            sub.start.minutes * 60000 + 
                            sub.start.seconds * 1000 + 
                            sub.start.milliseconds)
                
                end_time = (sub.end.hours * 3600000 + 
                          sub.end.minutes * 60000 + 
                          sub.end.seconds * 1000 + 
                          sub.end.milliseconds)
                
                duration = end_time - start_time

                # Skip if already exists
                if not os.path.exists(output_file):
                    rate = self.calculate_speech_rate(len(sub.text), duration)
                    await self.text_to_speech(sub.text, output_file, rate)
                else:
                    rate = "cached"

                segment = TTSSegment(
                    file_path=output_file,
                    start_time=start_time,
                    end_time=end_time,
                    text=sub.text,
                    rate=rate
                )
                segments.append(segment)

                # Update progress
                self._progress = int((i + 1) / total_subs * 100)
                self.notify_observers("progress", self._progress)

            self._current_segments = segments
            self._is_generating = False
            self.notify_observers("generation_complete", segments)
            return segments

        except Exception as e:
            self._is_generating = False
            self.notify_observers("generation_error", str(e))
            raise e

    def clear_segments(self):
        """Clear current segments"""
        self._current_segments.clear()
        self.notify_observers("segments_cleared")
