from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt, QPoint

class TitleBar(QWidget):

    def __init__(self, parent):
        super(TitleBar, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        """TitleBar UI 초기화 메서드"""
        # 수평 레이아웃 초기화
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # 타이틀 라벨 설정
        self.title = QLabel("My Own Bar")
        self.title.setFixedHeight(40)
        self.title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title.setStyleSheet(f"""
            padding: 10px;
        """)

        # 버튼 설정 및 스타일 적용
        btn_size = 35
        self.btn_close = self.createButton("x", self.btn_close_clicked, btn_size)
        self.btn_min = self.createButton("-", self.btn_min_clicked, btn_size)

        # 레이아웃에 위젯 추가
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_close)

        self.setLayout(self.layout)
        
        # 마우스 이벤트 처리를 위한 변수 초기화
        self.start = QPoint(0, 0)
        self.pressing = False

    def createButton(self, text, clicked, size, bg_color):
        """버튼 생성 및 스타일 적용 메서드"""
        button = QPushButton(text)
        button.clicked.connect(clicked)
        button.setFixedSize(size, size)
        button.setStyleSheet(f"""
            background-color: {bg_color};
            font-size: 18px;
            border: none;
        """)
        # 호버 시 배경색 변경
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                font-size: 18px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.darkenColor(bg_color)};
            }}
        """)
        return button

    def darkenColor(self, color):
        """Color을 약간 어둡게 만드는 함수"""
        r, g, b = self.hex_to_rgb(color)
        r = max(0, r - 10)
        g = max(0, g - 10)
        b = max(0, b - 10)
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def hex_to_rgb(self, color):
        """Hex color를 RGB 튜플로 변환하는 함수"""
        color = color.lstrip('#')
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

    def resizeEvent(self, QResizeEvent):
        """위젯 크기 변경 이벤트 핸들러"""
        super(TitleBar, self).resizeEvent(QResizeEvent)
        self.title.setFixedWidth(self.parent.width())

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 핸들러"""
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        """마우스 드래그 이벤트 핸들러"""
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.parent.setGeometry(
                self.mapToGlobal(self.movement).x(),
                self.mapToGlobal(self.movement).y(),
                self.parent.width(),
                self.parent.height()
            )
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        """마우스 클릭 해제 이벤트 핸들러"""
        self.pressing = False

    def btn_close_clicked(self):
        """닫기 버튼 클릭 이벤트 핸들러"""
        self.parent.close()

    def btn_min_clicked(self):
        """최소화 버튼 클릭 이벤트 핸들러"""
        self.parent.showMinimized()
