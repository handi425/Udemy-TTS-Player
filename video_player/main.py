import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication
from mvc.models.video_model import VideoModel
from mvc.models.tts_model import TTSModel
from mvc.models.player_model import PlayerModel
from mvc.controllers.player_controller import PlayerController
from mvc.views.player_view import PlayerView
import json

class VideoPlayerApp:
    def __init__(self):
        # Inisialisasi models
        self.video_model = VideoModel()
        self.tts_model = TTSModel()
        self.player_model = PlayerModel()

        # Inisialisasi controller
        self.controller = PlayerController(
            self.video_model,
            self.tts_model,
            self.player_model
        )

        # Inisialisasi view dan setup hubungan dengan controller
        self.view = PlayerView(self.controller)
        self.controller.setup_view(self.view)

        # Load saved playlist
        self.load_playlist()

    def load_playlist(self):
        """Load saved playlist from file"""
        try:
            with open('playlist.json', 'r') as f:
                data = json.load(f)
                self.controller.load_playlist(data)
        except:
            print("No saved playlist found")

    def save_playlist(self):
        """Save playlist to file"""
        try:
            data = self.controller.save_playlist()
            with open('playlist.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving playlist: {e}")

    def run(self):
        """Run the application"""
        self.view.show()

async def main():
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    # Create application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Setup asyncio loop
    loop = asyncio.get_event_loop()
    future = asyncio.Future()
    
    # Create and run video player
    player = VideoPlayerApp()
    player.run()
    
    # Setup cleanup
    app.aboutToQuit.connect(
        lambda: close_future(future, loop)
    )
    
    # Run event loop
    try:
        await future
    except asyncio.CancelledError:
        # Save playlist on exit
        player.save_playlist()

def run():
    try:
        qasync.run(main())
    except asyncio.CancelledError:
        sys.exit(0)

if __name__ == "__main__":
    run()
