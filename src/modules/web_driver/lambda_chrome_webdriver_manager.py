import os
from utils.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class ChromeWebDriverManager:
    """크롬 드라이버를 자동으로 관리하는 클래스"""
    
    CHROME_DRIVER_PATH = "/tmp/chromedriver"

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver_path = None
        self.setup_driver()

    def setup_driver(self):
        """드라이버를 /tmp 디렉토리에서 확인하고, 없으면 다운로드하는 메서드"""
        try:
            if os.path.exists(self.CHROME_DRIVER_PATH):
                logger.log("info", "기존 크롬 드라이버를 재사용합니다.")
                self.driver_path = self.CHROME_DRIVER_PATH
            else:
                logger.log("info", "새로운 크롬 드라이버를 다운로드합니다.")
                self.driver_path = ChromeDriverManager().install()
                # 다운로드된 드라이버를 /tmp로 복사
                import shutil
                shutil.copy2(self.driver_path, self.CHROME_DRIVER_PATH)
                self.driver_path = self.CHROME_DRIVER_PATH
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
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        # Lambda 환경에 최적화된 옵션
        options.binary_location = '/opt/chrome/chrome'  # Lambda Layer에 설치된 Chrome 위치
        options.add_argument("--disable-gpu")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-zygote")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-webgl")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-background-networking")

        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        logger.log("info", "크롬 드라이버 실행 완료")
        return driver 