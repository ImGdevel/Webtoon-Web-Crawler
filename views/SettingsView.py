from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QPushButton, QLabel, QSlider, QHBoxLayout, QLineEdit
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtCore import QTimer, Qt

class SettingsView(QWidget):
    def __init__(self, parent = None):

        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # 전체 레이아웃 설정
        self.layout = QVBoxLayout()

        #title
        self.page_title = QLabel("Setting")
        font = QFont('Arial', 50)  # 폰트 종류와 크기 설정
        nfont = QFont('Arial', 25)
        self.page_title.setFont(font)

        # 폴더 경로
        self.download_folder_setting = QWidget()
        self.download_setting_layout = QHBoxLayout()

        self.download_folder_label = QLabel("DownLoad Folder Path")
        self.download_folder_label.setFont(nfont)
        
        self.download_folder_widget = QWidget()
        self.download_folder_layout = QHBoxLayout()
        self.download_folder_btn = QPushButton('파일 선택', self)
        self.download_folder_btn.clicked.connect(self.showFolderDialog)
        self.download_folder_line = QLineEdit(self)
        self.download_folder_line.setReadOnly(True)
        self.download_folder_layout.addWidget(self.download_folder_line)
        self.download_folder_layout.addWidget(self.download_folder_btn)
        self.download_folder_widget.setLayout(self.download_folder_layout)

        self.download_setting_layout.addWidget(self.download_folder_label)
        self.download_setting_layout.addWidget(self.download_folder_widget)
        self.download_folder_setting.setLayout(self.download_setting_layout)


        # 모자이크 정도 조절 설정 
        self.mosaic_setting = QWidget()
        self.mosaic_setting_layer = QHBoxLayout()

        self.mosaic_degree_label = QLabel("Mosaic Degree")
        self.mosaic_degree_label.setFont(nfont)
        
        self.mosaic_degree_widget = QWidget()
        self.mosaic_degree_layer = QHBoxLayout()
        self.mosaic_degree_count = QLabel('값: 0', self) 
        self.mosaic_degree_count.setFont(nfont)
        self.mosaic_slider = QSlider(Qt.Horizontal, self)
        self.mosaic_slider.setMinimum(0)
        self.mosaic_slider.setMaximum(100)
        self.mosaic_slider.setValue(0)
        self.mosaic_slider.valueChanged.connect(self.onSlide)
        self.mosaic_degree_layer.addWidget(self.mosaic_degree_count)
        self.mosaic_degree_layer.addWidget(self.mosaic_slider)
        self.mosaic_degree_widget.setLayout(self.mosaic_degree_layer)
        
        self.mosaic_setting_layer.addWidget(self.mosaic_degree_label)
        self.mosaic_setting_layer.addWidget(self.mosaic_degree_widget)
        self.mosaic_setting.setLayout(self.mosaic_setting_layer)

        # 레이아웃 설정
        self.layout.addWidget(self.page_title)
        self.layout.addWidget(self.download_folder_setting)
        self.layout.addWidget(self.mosaic_setting)
        self.setLayout(self.layout)

        # 창 설정
        self.setWindowTitle('파일 경로 선택기')
        self.setGeometry(300, 300, 400, 200)
        self.show()
    
    def render(self):
        """페이지 refesh"""
        pass
    
    def showFolderDialog(self):
        # 파일 선택 다이얼로그
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", "", options=options)
        if folder:
            self.download_folder_line.setText(folder)

    def onSlide(self, value):
        self.mosaic_degree_count.setText(f'값: {value}')
