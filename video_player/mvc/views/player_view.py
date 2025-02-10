import os
import asyncio
from typing import Optional, Callable, Any
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QTimer
from .modern_player_window import ModernPlayerWindow

class PlayerView:
    def __init__(self, controller: Any):
        self.controller = controller
        self.window = ModernPlayerWindow()
        self.setup_connections()
        
        # Setup event loop
        self.loop = asyncio.get_event_loop()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.setInterval(50)  # 50ms for smooth updates
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start()

        # TTS observer registration
        if hasattr(self.controller, 'tts_model'):
            self.controller.tts_model.add_observer(self)
        if hasattr(self.controller, 'video_model'):
            self.controller.video_model.add_observer(self)
        if hasattr(self.controller, 'player_model'):
            self.controller.player_model.add_observer(self)

    # Properti untuk akses ke elemen UI dari ModernPlayerWindow
    @property
    def play_button(self):
        return self.window.play_button

    @property
    def prev_button(self):
        return self.window.prev_button

    @property
    def next_button(self):
        return self.window.next_button

    @property
    def volume_slider(self):
        return self.window.volume_slider

    @property
    def tts_toggle(self):
        return self.window.tts_toggle
        
    @property
    def source_language(self):
        return self.window.source_language
        
    @property
    def target_language(self):
        return self.window.target_language

    @property
    def progress_bar(self):
        return self.window.progress_bar
        
    @property
    def playlist(self):
        return self.window.playlist

    @property
    def add_button(self):
        return self.window.add_button

    @property
    def remove_button(self):
        return self.window.remove_button

    @property
    def voice_selector(self):
        return self.window.voice_selector

    @property
    def video_frame(self):
        return self.window.video_frame

    def setup_connections(self):
        """Setup UI event connections"""
        # Playback controls
        self.window.play_button.clicked.connect(self.toggle_playback)
        self.window.next_button.clicked.connect(
            lambda: self.loop.create_task(self.next_video())
        )
        self.window.prev_button.clicked.connect(
            lambda: self.loop.create_task(self.previous_video())
        )
        
        # TTS controls
        self.window.tts_toggle.clicked.connect(self.toggle_tts)
        self.window.voice_selector.currentTextChanged.connect(self.voice_changed)
        
        # Playlist controls
        self.window.add_button.clicked.connect(self.add_video)
        self.window.remove_button.clicked.connect(self.remove_video)
        self.window.playlist.currentRowChanged.connect(
            lambda idx: self.loop.create_task(self.playlist_item_changed(idx))
        )
        
        # Media controls
        self.window.progress_bar.sliderMoved.connect(self.seek)
        self.window.volume_slider.valueChanged.connect(self.volume_changed)

    async def next_video(self):
        """Play next video"""
        await self.controller.next_video(self.window.get_video_frame().winId())

    async def previous_video(self):
        """Play previous video"""
        await self.controller.previous_video(self.window.get_video_frame().winId())

    def toggle_playback(self):
        """Toggle play/pause"""
        self.controller.toggle_playback()

    def toggle_tts(self):
        """Toggle TTS audio"""
        state = self.controller.player_model.state
        self.controller.toggle_tts(not state.is_using_tts)

    def seek(self, position: int):
        """Seek video position"""
        self.controller.seek_video(position / 1000.0)

    def volume_changed(self, value: int):
        """Handle volume change"""
        self.controller.set_volume(value)

    def voice_changed(self, voice_type: str):
        """Handle voice type change"""
        self.controller.tts_model.set_voice_type(
            "pria" if voice_type == "Male" else "wanita"
        )

    def add_video(self):
        """Add new video to playlist"""
        video_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "Select Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv);;All Files (*.*)"
        )
        
        if video_path:
            srt_path, _ = QFileDialog.getOpenFileName(
                self.window,
                "Select Subtitle",
                "",
                "Subtitle Files (*.srt);;All Files (*.*)"
            )
            
            if srt_path:
                voice_type = "pria" if self.window.voice_selector.currentText() == "Male" else "wanita"
                # Hanya tambahkan video ke model, UI akan diupdate melalui observer
                self.controller.add_video(video_path, srt_path, voice_type)

    def remove_video(self):
        """Remove video from playlist"""
        current = self.window.playlist.currentRow()
        if current >= 0:
            self.controller.remove_video(current)
            self.window.playlist.takeItem(current)

    async def playlist_item_changed(self, index: int):
        """Handle playlist item selection"""
        if index >= 0:
            await self.controller.play_video(self.window.get_video_frame().winId())

    def update_ui(self):
        """Update status UI berdasarkan state player"""
        if not self.controller:
            return
            
        state = self.controller.player_model.state
        if state:
            # Update time display
            self.update_time_label(state.current_time, state.duration)
            
            # Update progress bar
            if state.duration > 0:
                progress = int((state.current_time / state.duration) * 1000)
                self.window.progress_bar.setValue(progress)
            
            # Update play button
            self.set_playing(state.is_playing)
            
            # Update TTS button
            self.set_tts_enabled(state.is_using_tts)

    def on_tts_update(self, event_type: str, data=None):
        """Handle TTS events"""
        if event_type == "generation_started":
            self.window.tts_progress.setVisible(True)
            self.window.tts_progress.setValue(0)
        elif event_type == "progress":
            self.window.tts_progress.setValue(data)
        elif event_type == "generation_complete":
            self.window.tts_progress.setVisible(False)
        elif event_type == "generation_error":
            QMessageBox.critical(self.window, "Error", f"TTS Generation failed: {data}")

    def on_player_update(self, event_type: str, data=None):
        """Handle player events"""
        if event_type == "error":
            QMessageBox.critical(self.window, "Error", str(data))

    def on_model_updated(self):
        """Handle model updates"""
        # Refresh playlist display
        self.window.playlist.clear()
        for video in self.controller.video_model._videos:
            self.window.playlist.addItem(os.path.basename(video.video_path))

    def show(self):
        """Show the main window"""
        self.window.show()

    def update_progress(self, value: int):
        """Update progress bar untuk konversi TTS"""
        self.window.update_progress(value)

    def update_source_models(self, models):
        """Update model yang tersedia untuk bahasa sumber"""
        self.window.update_source_models(models)

    def update_target_models(self, models):
        """Update model yang tersedia untuk bahasa target"""
        self.window.update_target_models(models)

    def show_loading(self, show: bool):
        """Menampilkan atau menyembunyikan loading indicator"""
        self.window.show_loading(show)

    def update_time_label(self, current: int, total: int):
        """Update label waktu"""
        self.window.update_time_label(current, total)

    def set_playing(self, is_playing: bool):
        """Update status tombol play"""
        self.window.set_playing(is_playing)

    def set_tts_enabled(self, enabled: bool):
        """Update status tombol TTS"""
        self.window.set_tts_enabled(enabled)
