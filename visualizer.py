from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtCore import QTimer
import numpy as np
import random

class Visualizer(QWidget):
    def __init__(self, analyzer, parent=None):
        super().__init__(parent)
        self.analyzer = analyzer

        # Q — состояние визуализации
        self.state = None
        self.current_features = None

        # Таймер для обновления экрана
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 мс ~ 33 кадра/сек

        self.current_features = None

    def update_frame(self):
        if self.analyzer.data_ready():
            features = self.analyzer.get_next_frame()
            self.update_data(features)
        self.update()


    def update_data(self, features):
        self.current_features = features
        if self.state is None:
            self.state = {
                'radius': 50,
                'hue': 0,
                'x_offset': 0,
                'y_offset': 0
            }

        # F(M[t]) — преобразование аудио в изменения параметров
        delta_radius = features['rms'] * 100
        delta_hue = features['centroid'] * 0.00005
        delta_x = (np.random.rand() - 0.5) * 20 * features['zcr']
        delta_y = (np.random.rand() - 0.5) * 20 * features['zcr']

        # Q[t+1] = Q[t] + F(M[t])
        self.state['radius'] = max(10, self.state['radius'] * 0.9 + delta_radius)
        self.state['hue'] = self.state['hue'] + delta_hue
        self.state['x_offset'] = self.state['x_offset'] * 0.9 + delta_x
        self.state['y_offset'] = self.state['y_offset'] * 0.9 + delta_y

        self.update()

    def paintEvent(self, event):
        if self.state is None:
            return

        painter = QPainter(self)
        width = self.width()
        height = self.height()

        color = QColor.fromHsv(int(self.state['hue']) % 360, 255, 255)
        painter.setBrush(QBrush(color))
        painter.setPen(QColor(0, 0, 0, 0))

        cx = width // 2 + int(self.state['x_offset'])
        cy = height // 2 + int(self.state['y_offset'])
        r = int(self.state['radius'])

        painter.drawEllipse(cx - r // 2, cy - r // 2, r, r)
