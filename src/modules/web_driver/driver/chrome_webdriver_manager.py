from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from .web_driver_manager import WebDriverManager

class ChromeWebDriverManager(WebDriverManager):
    """로컬 환경에서 Chrome WebDriver를 관리하는 클래스"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless

    def get_driver(self):
        """Chrome WebDriver 인스턴스를 생성하고 반환합니다."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # 기본 옵션 설정
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # ChromeDriver 자동 설치 및 서비스 생성
        service = Service(ChromeDriverManager().install())
        
        # WebDriver 생성
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver 