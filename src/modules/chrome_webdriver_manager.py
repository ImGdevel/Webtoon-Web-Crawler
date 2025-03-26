from logger import Logger 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = Logger()

class ChromeWebDriverManager:
    """크롬 드라이버를 자동으로 관리하는 클래스"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver_path = None
        self.setup_driver()

    def setup_driver(self):
        """드라이버를 자동으로 다운로드하고 설정하는 메서드"""
        try:
            self.driver_path = ChromeDriverManager().install()
            logger.log("info", "크롬 드라이버 설치 완료")
        except Exception as e:
            logger.log("error", f"크롬 드라이버 설치 오류: {e}")

    def get_driver(self):
        """설정된 크롬 드라이버를 반환하는 메서드"""
        if not self.driver_path:
            logger.log("warning", "크롬 드라이버를 찾을 수 없습니다. 다시 설정합니다.")
            self.setup_driver()

        options = Options()
        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        logger.log("info", "크롬 드라이버 실행 완료")
        return driver 