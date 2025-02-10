import asyncio
import edge_tts
import pysrt
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import pyttsx3
import json
from PyQt5.QtCore import QObject, pyqtSignal
import speech_recognition as sr
from googletrans import Translator

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

class TTSModel(QObject):
    conversion_progress = pyqtSignal(int)  # Signal untuk progress konversi
    conversion_complete = pyqtSignal()      # Signal ketika konversi selesai
    
    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.translator = Translator()
        self.available_languages = self._get_available_languages()
        self.current_source_lang = 'en'     # Bahasa default source
        self.current_target_lang = 'id'     # Bahasa default target
        self._observers = []
        self._current_segments: List[TTSSegment] = []
        self._is_generating = False
        self._progress = 0
        self._voice_type = "pria"
        self._global_speed = 1.15

    def _get_available_languages(self):
        """Mendapatkan daftar bahasa yang tersedia"""
        # Format: {'code': {'name': 'Bahasa Name', 'models': ['model1', 'model2']}}
        return {
            'en': {'name': 'English', 'models': ['en-us', 'en-uk']},
            'id': {'name': 'Indonesian', 'models': ['id']},
            'ja': {'name': 'Japanese', 'models': ['ja']},
            'ko': {'name': 'Korean', 'models': ['ko']}
        }
    
    def set_language(self, source_lang, target_lang):
        """Mengatur bahasa source dan target"""
        if source_lang in self.available_languages and target_lang in self.available_languages:
            self.current_source_lang = source_lang
            self.current_target_lang = target_lang
            return True
        return False
    
    def convert_srt_to_audio(self, srt_path, output_path):
        """Mengkonversi file SRT ke audio dengan loading progress"""
        try:
            with open(srt_path, 'r', encoding='utf-8') as file:
                subtitles = file.readlines()
            
            total_lines = len(subtitles)
            current_line = 0
            
            # Proses tiap line subtitle
            for line in subtitles:
                if line.strip():  # Skip baris kosong
                    # Translate text jika bahasa berbeda
                    if self.current_source_lang != self.current_target_lang:
                        translated = self.translator.translate(
                            line.strip(),
                            src=self.current_source_lang,
                            dest=self.current_target_lang
                        )
                        text = translated.text
                    else:
                        text = line.strip()
                    
                    self.engine.save_to_file(text, output_path)
                
                current_line += 1
                progress = int((current_line / total_lines) * 100)
                self.conversion_progress.emit(progress)
            
            self.conversion_complete.emit()
            return True
            
        except Exception as e:
            print(f"Error dalam konversi SRT ke audio: {str(e)}")
            return False
    
    def merge_video_and_audio(self, video_path, audio_path, output_path):
        """Menggabungkan video dengan audio TTS"""
        try:
            import ffmpeg
            
            # Dapatkan durasi video
            probe = ffmpeg.probe(video_path)
            video_duration = float(probe['streams'][0]['duration'])
            
            # Sesuaikan audio dengan durasi video
            stream = ffmpeg.input(audio_path)
            stream = ffmpeg.filter(stream, 'atempo', video_duration/float(probe['streams'][1]['duration']))
            
            # Gabungkan video dengan audio yang sudah disesuaikan
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(stream['v'], stream['a'], output_path)
            ffmpeg.run(stream, overwrite_output=True)
            
            return True
        except Exception as e:
            print(f"Error dalam penggabungan video dan audio: {str(e)}")
            return False
    
    def get_available_models(self, lang_code):
        """Mendapatkan model yang tersedia untuk bahasa tertentu"""
        if lang_code in self.available_languages:
            return self.available_languages[lang_code]['models']
        return []

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
