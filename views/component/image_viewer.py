from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QVBoxLayout, QScrollArea
from PySide6.QtCore import Qt, QUrl, Signal
from .image_item import ImageItem
import os

class ImageViewWidget(QWidget):
    count = int
    remove_image_event = Signal(QUrl)
    add_image_event = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.remove_mode = False
        self.count = 0
        self.layout = QVBoxLayout()
        #file view
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.file_view_widget = QWidget()
        self.scroll_widget = QWidget()
        self.file_box_layout = QHBoxLayout()
        
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.file_box_layout.addWidget(self.scroll_area)
        self.file_view_widget.setLayout(self.file_box_layout)

        #set frame layout
        self.layout.addWidget(self.file_view_widget)
        self.setLayout(self.layout)
        

    def openFileExplorer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "이미지 파일 (*.bmp *.dng *.jpeg *.jpg *.mpo *.png *.tif *.tiff *.webp *.pnm)"
        fname = QFileDialog()
        fname.setFileMode(QFileDialog.ExistingFiles)
        fname.setNameFilter(filters)
        if fname.exec_():
            selected_files = fname.selectedFiles()
            file_list = list()
            # Process selected files
            for file_path in selected_files:
                _, extension = os.path.splitext(file_path)
                if extension.lower() in ['.bmp', '.dng', '.jpeg', '.jpg', '.mpo', '.png', '.tif', '.tiff', '.webp', '.pnm']:
                    file_info = QUrl.fromLocalFile(file_path)
                    file_list.append(file_info)
            self.add_image_event.emit(file_list)

    def addNewFile(self, urls):
        for i, file_info in enumerate(urls):
            file_widget = ImageItem(file_info)
            file_widget.delet_signal.connect(self.removeFile)
            file_widget.setFixedSize(100, 100)
            self.scroll_layout.addWidget(file_widget)
            self.count += 1

    def removeFile(self, widget):
        if self.remove_mode:
            self.remove_file.emit(widget.getUrl())
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()


