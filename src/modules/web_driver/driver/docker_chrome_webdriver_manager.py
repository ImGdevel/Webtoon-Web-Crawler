import os
from utils.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .web_driver_manager import WebDriverManager

class DockerChromeWebDriverManager(WebDriverManager):
    """Docker Lambda 환경에서 Chrome WebDriver를 관리하는 클래스"""
    
    def __init__(self):
        self.chrome_binary = os.getenv('CHROME_BIN', '/usr/bin/chromium')
        self.chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')

    def get_driver(self):
        """Chrome WebDriver 인스턴스를 생성하고 반환합니다."""
        chrome_options = Options()
        
        # Docker Lambda 환경에 필요한 옵션 설정
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.binary_location = '/usr/bin/chromium'
        
        # Chrome 서비스 생성
        service = Service(
            executable_path='/usr/bin/chromedriver',
        )
        
        # Chrome WebDriver 생성
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        return driver

    def setup_driver(self):
        """드라이버 설정을 확인하는 메서드"""
        try:
            if not os.path.exists(self.chrome_binary):
                raise FileNotFoundError(f"Chrome 바이너리를 찾을 수 없습니다: {self.chrome_binary}")
            if not os.path.exists(self.chromedriver_path):
                raise FileNotFoundError(f"ChromeDriver를 찾을 수 없습니다: {self.chromedriver_path}")
            
            logger.info("Docker Lambda 환경의 크롬 드라이버 설정 확인 완료")
        except Exception as e:
            logger.error("크롬 드라이버 설정 확인 중 오류 발생", error=e)
            raise 