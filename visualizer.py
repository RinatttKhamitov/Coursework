from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class VisualWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = [0] * 100

    def update_data(self, new_data):
        self.data = new_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()
        bar_width = width / len(self.data)
        for i, value in enumerate(self.data):
            painter.setPen(QColor(100, 200, 255))
            x = int(i * bar_width)
            y = int(height - value * height)
            painter.drawLine(x, height, x, y)