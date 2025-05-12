from PyQt5.QtWidgets import QMainWindow, QPushButton, QFileDialog, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from visualizer import VisualWidget
from analyzer import AudioAnalyzer
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Visualizer")
        self.setGeometry(100, 100, 800, 600)

        self.visual = VisualWidget()
        self.analyzer = AudioAnalyzer()

        # Создаём кнопку для загрузки музыки
        btn = QPushButton("Load Audio")
        btn.clicked.connect(self.load_audio)

        layout = QVBoxLayout()
        layout.addWidget(btn)
        layout.addWidget(self.visual)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Создаём таймер для обновления визуализации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_visual)
        self.timer.start(30)  # Таймер обновляется каждые 30 миллисекунд

        # Для синхронизации
        self.start_time = None  # Время старта воспроизведения
        self.audio_time = 0  # Время воспроизведения

        # Добавляем медиаплеер
        self.player = QMediaPlayer(self)

    def load_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Audio", "", "WAV Files (*.wav)")
        if path:
            # Загружаем аудио
            self.analyzer.load_audio(path)
            
            # Настроим медиаплеер
            url = QUrl.fromLocalFile(path)
            content = QMediaContent(url)
            self.player.setMedia(content)

            # Включаем воспроизведение
            self.player.play()

            # Запускаем отсчёт времени
            self.start_time = time.time()  # Устанавливаем начальное время

    def update_visual(self):
        if self.start_time is None:
            return

        # Вычисляем время прошедшее с начала воспроизведения
        elapsed_time = time.time() - self.start_time
        self.audio_time = elapsed_time

        # Синхронизируем индексы с временем
        index = int(self.audio_time * self.analyzer.samplerate)
        
        # Если время выходит за пределы длины трека, останавливаем визуализацию
        if index >= len(self.analyzer.samples):
            self.timer.stop()
            return
        
        # Считываем данные для текущего времени
        self.analyzer.index = index
        if self.analyzer.data_ready():
            self.visual.update_data(self.analyzer.get_next_frame())
