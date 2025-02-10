from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QFileDialog,
    QSlider, QComboBox, QProgressBar, QFrame,
    QStackedWidget, QStyle
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QPalette, QColor

class ModernPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Video Player with TTS")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        """Setup modern styling"""
        # Dark theme colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
            QSlider::groove:horizontal {
                border: 1px solid #4d4d4d;
                height: 4px;
                background: #2d2d2d;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: none;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }
            QProgressBar {
                border: none;
                background-color: #2d2d2d;
                text-align: center;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 2px;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Left panel (Video and Controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Video frame
        self.video_frame = QFrame()
        self.video_frame.setFrameStyle(QFrame.Shape.Box)
        self.video_frame.setStyleSheet("background-color: black;")
        left_layout.addWidget(self.video_frame, stretch=1)

        # Progress bar
        progress_layout = QHBoxLayout()
        self.time_label = QLabel("00:00 / 00:00")
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.time_label)
        left_layout.addLayout(progress_layout)

        # Controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Control buttons with icons
        self.prev_button = QPushButton("⏮")
        self.play_button = QPushButton("▶")
        self.next_button = QPushButton("⏭")
        self.tts_toggle = QPushButton("TTS Off")
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_icon = QPushButton("🔊")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        volume_layout.addWidget(volume_icon)
        volume_layout.addWidget(self.volume_slider)

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.tts_toggle)
        controls_layout.addLayout(volume_layout)
        controls_layout.addStretch()

        left_layout.addWidget(controls)

        # TTS Generation Progress
        self.tts_progress = QProgressBar()
        self.tts_progress.setVisible(False)
        left_layout.addWidget(self.tts_progress)

        # Right panel (Playlist)
        right_panel = QWidget()
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout(right_panel)

        # Playlist controls
        playlist_controls = QHBoxLayout()
        self.add_button = QPushButton("Add Video")
        self.remove_button = QPushButton("Remove")
        playlist_controls.addWidget(self.add_button)
        playlist_controls.addWidget(self.remove_button)
        right_layout.addLayout(playlist_controls)

        # Voice selector
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_selector = QComboBox()
        self.voice_selector.addItems(["Male", "Female"])
        voice_layout.addWidget(self.voice_selector)
        right_layout.addLayout(voice_layout)

        # Playlist
        self.playlist = QListWidget()
        right_layout.addWidget(self.playlist)

        # Add panels to main layout
        layout.addWidget(left_panel, stretch=7)
        layout.addWidget(right_panel, stretch=3)

    def set_tts_progress(self, value: int):
        """Update TTS generation progress"""
        self.tts_progress.setVisible(value < 100)
        self.tts_progress.setValue(value)

    def format_time(self, ms: int) -> str:
        """Format milliseconds to MM:SS"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update_time_label(self, current: int, total: int):
        """Update time display"""
        self.time_label.setText(
            f"{self.format_time(current)} / {self.format_time(total)}"
        )

    def set_playing(self, is_playing: bool):
        """Update play button state"""
        self.play_button.setText("Pause" if is_playing else "Play")

    def set_tts_enabled(self, enabled: bool):
        """Update TTS button state"""
        self.tts_toggle.setText("TTS On" if enabled else "TTS Off")

    def get_video_frame(self) -> QFrame:
        """Get video frame widget"""
        return self.video_frame
