from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer, Qt

class HomeView(QWidget):
    def __init__(self, parent = None):

        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # 전체 레이아웃 설정
        self.layout = QHBoxLayout()
        self.label = QLabel("My Page")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
    
    def render(self):
        """페이지 refesh"""
        pass
