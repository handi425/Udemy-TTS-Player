from setuptools import setup, find_packages

setup(
    name="video_player",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'python-vlc',
        'edge-tts',
        'pysrt',
        'pydub',
        'qasync'
    ],
)
