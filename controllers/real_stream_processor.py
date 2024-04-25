import cv2
from PySide6.QtGui import QImage
from PySide6.QtCore import QThread, Signal
from models import Filtering, FilterManager

# 비디오 처리 스레드
class RealStreamProcessor(QThread):
    frame_ready = Signal(QImage)

    def __init__(self):
        super().__init__()
        self.video_cap = cv2.VideoCapture(0)  # 웹캠 캡처 객체
        self.filtering = Filtering()
        self.filter_manager = FilterManager()

        self.current_filter = None
        
        self.is_running = False  # 스레드 실행 상태
        self.is_flipped = False  # 화면 좌우 뒤집기 상태
        self.mosaic_active = False  # 모자이크 활성화 상태

    def run(self):
        '''스레드 실행 메서드 - 웹캠에서 프레임을 읽어와 RGB 형식으로 변환.'''
        self.is_running = True
        while self.is_running:
            ret, frame = self.video_cap.read()  # 웹캠에서 프레임 읽기
            if ret:
                processed_frame = self.process_frame(frame)  # 프레임 처리
                
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)  # BGR을 RGB로 변환

                if self.is_flipped:
                    frame_rgb = cv2.flip(frame_rgb, 1)  # 화면 좌우 뒤집기

                height, width, channel = frame_rgb.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.frame_ready.emit(q_img)  # 프레임을 GUI로 전송
            self.msleep(16)  # 약 60fps

    def process_frame(self, frame):
        '''프레임 처리 메서드 - 얼굴 모자이크 및 객체 인식'''
        processed_frame = frame
        if not self.current_filter is None:
            boxesList = self.filtering.video_filtering(frame, self.current_filter)    
            processed_frame = self.filtering.elliptical_blur(frame, boxesList)
    
        return processed_frame
    
    def set_filter(self, filter):
        """필터 설정"""
        if not filter is None:
            self.current_filter = self.filter_manager.get_filter(filter)
            print("현제 적용 필터 :",  self.current_filter)

    def flip_horizontal(self):
        '''화면 좌우 뒤집기 메서드'''
        self.is_flipped = not self.is_flipped  # 화면 좌우 뒤집기 상태 변경

    def stop(self):
        '''스레드 종료 메서드'''
        self.is_running = False
        self.wait()
