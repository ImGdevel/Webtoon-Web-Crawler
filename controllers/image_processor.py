from PySide6.QtGui import QImage
from PySide6.QtCore import QThread, Signal
import cv2
import os
from datetime import datetime
import numpy as np

# 비디오 처리 스레드
class ImageProcessor(QThread):

    def __init__(self):
        super().__init__()
        pass


    #원본 사진을 받아서 임시로 이미지 처리
    def filtering_images(self, image_paths):
        pass

    #원본 사진을 받아서 임시로 이미지 처리
    def filtering_images_to_dict(self, image_paths):
        pass

    def QImage_to_cv2(qimage):
        """
        QImage를 numpy 배열로 변환합니다.
        
        Args:
        - qimage: 변환할 QImage 객체
        
        Returns:
        - 변환된 numpy 배열
        """
        pass


    def create_filtered_image(self, QImage_list):
        pass

    def set_filter(self, filter):
        """필터 설정"""
        pass

            