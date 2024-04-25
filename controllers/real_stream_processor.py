from PySide6.QtGui import QImage
from PySide6.QtCore import QThread, Signal
import cv2

# 비디오 처리 스레드
class RealStreamProcessor(QThread):
    frame_ready = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.video_cap = cv2.VideoCapture(0)  # 웹캠 캡처 객체

    def run(self):
        '''스레드 실행 메서드 - 웹캠에서 프레임을 읽어와 RGB 형식으로 변환.'''
        pass

    def process_frame(self, frame):
        '''프레임 처리 메서드 - 얼굴 모자이크 및 객체 인식'''
        processed_frame = frame
    
        return processed_frame
    
    def set_filter(self, filter):
        """필터 설정"""
        pass

    def flip_horizontal(self):
        '''화면 좌우 뒤집기 메서드'''
        pass

    def stop(self):
        '''스레드 종료 메서드'''
        pass
