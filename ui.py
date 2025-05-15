from PyQt5.QtWidgets import QMainWindow, QPushButton, QFileDialog, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from visualizer import Visualizer  # Новый визуализатор!
from analyzer import AudioAnalyzer
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Visualizer")
        self.setGeometry(100, 100, 800, 600)

        self.analyzer = AudioAnalyzer()
        self.visual = Visualizer(self.analyzer)  # Передаём анализатор внутрь визуализатора

        # Кнопка загрузки музыки
        btn = QPushButton("Load Audio")
        btn.clicked.connect(self.load_audio)

        layout = QVBoxLayout()
        layout.addWidget(btn)
        layout.addWidget(self.visual)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Таймер для синхронизации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sync_audio)
        self.timer.start(30)

        self.start_time = None
        self.audio_time = 0
        self.player = QMediaPlayer(self)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Audio", "", "WAV Files (*.wav)")
        if path:
            self.analyzer.load_audio(path)

            url = QUrl.fromLocalFile(path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
            self.start_time = time.time()

    def sync_audio(self):
        if self.start_time is None:
            return

        elapsed_time = time.time() - self.start_time
        self.audio_time = elapsed_time

        index = int(self.audio_time * self.analyzer.samplerate)

        if index >= len(self.analyzer.samples):
            self.timer.stop()
            return

        self.analyzer.index = index
