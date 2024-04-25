import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage, QPixmap
import shutil

class VideoProcessor(QThread):
    '''비디오 재생을 위한 스레드 클래스'''
    video_frame = Signal(object)  # 비디오 프레임 신호
    current_frame = Signal(int)    # 현재 프레임 신호
    fps_signal = Signal(float)     # FPS 신호

    def __init__(self):
        super().__init__()
        self.temp_video_path = str
        
        self.current_filter = None
        self.is_playing = False
        self.is_video_ready = False

    def set_video(self, video_path):
        """재생할 비디오를 세팅합니다"""
        pass

    def run(self):
        self.is_playing = True
        '''비디오 재생 스레드의 메인 루프'''
        pass
    
    def play_video(self):
        """비디오를 재생합니다"""
        pass

    def puse_video(self):
        """비디오를 일시정지 합니다"""

        pass

    # 동영상 받아서 필터링된 동영상 파일 임시 생성
    def filtering_video(self):
        pass

    def download_video(self):
        """필터링 된 비디오를 다운합니다."""
        pass

    def set_filter(self, filter):
        """필터 설정"""
        pass