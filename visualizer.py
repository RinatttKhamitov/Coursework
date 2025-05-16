from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import QTimer, Qt
import numpy as np
import random

class Visualizer(QWidget):
    def __init__(self, analyzer, parent=None):
        super().__init__(parent)
        self.analyzer = analyzer
        self.frame = None
        self.features = None

        # Q — состояние визуализации
        self.state = {
            'radius': 50.0,
            'hue': 0.0,
            'x_offset': 0.0,
            'y_offset': 0.0,
            'bars': np.zeros(64)
        }

        # Таймер для обновления экрана
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~33 fps

    def update_frame(self):
        if self.analyzer.data_ready():
            data = self.analyzer.get_next_frame()
            self.features = data
            self.frame = data["frame"]
            self.update_state(data)
        self.update()

    def update_state(self, data):
        print(self.state)
        alpha = 0.9
        self.state['radius'] = alpha * self.state['radius'] + (1 - alpha) * (50 + data["rms"] * 300)
        self.state['hue'] = (self.state['hue'] + (data["centroid"] / 5000.0) * 5) % 360
        self.state['x_offset'] = self.state['x_offset'] * 0.8 + (np.random.rand() - 0.5) * data["zcr"] * 30
        self.state['y_offset'] = self.state['y_offset'] * 0.8 + (np.random.rand() - 0.5) * data["zcr"] * 30

        # Обновляем частотные полосы (баров 64)
        full_spectrum = np.array(data["spectrum"])
        bins = np.interp(np.linspace(0, len(full_spectrum), 64), np.arange(len(full_spectrum)), full_spectrum)
        self.state['bars'] = self.state['bars'] * 0.7 + bins * 0.5

    def paintEvent(self, event):
        if self.frame is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        center_x = width // 2 + int(self.state['x_offset'])
        center_y = height // 2 + int(self.state['y_offset'])

        # Фон
        painter.fillRect(self.rect(), Qt.black)

        # Цвет от hue
        color = QColor.fromHsv(int(self.state['hue']), 255, 255)

        # Пульсирующий круг
        painter.setBrush(QBrush(color))
        painter.setPen(QColor(0, 0, 0, 0))
        r = int(self.state['radius'])
        painter.drawEllipse(center_x - r // 2, center_y - r // 2, r, r)

        # Волна сигнала
        waveform = self.frame
        painter.setPen(QPen(Qt.white, 1))
        path_height = 150
        step = width / len(waveform)
        for i in range(len(waveform) - 1):
            x1 = i * step
            x2 = (i + 1) * step
            y1 = center_y + waveform[i] * path_height
            y2 = center_y + waveform[i+1] * path_height
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Спектрограмма
        bar_width = width / len(self.state['bars'])
        painter.setPen(Qt.NoPen)
        for i, val in enumerate(self.state['bars']):
            bar_height = val * 200
            painter.setBrush(QColor.fromHsv((int(self.state['hue']) + i * 6) % 360, 255, 255))
            x = int(i * bar_width)
            painter.drawRect(x, int(height - bar_height), int(bar_width - 1), int(bar_height))
