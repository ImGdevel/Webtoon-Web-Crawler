import os
from utils.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from ..common.i_web_driver_manager import IWebDriverManager

class DockerChromeWebDriverManager(IWebDriverManager):
    """Docker Lambda 환경에서 크롬 드라이버를 관리하는 클래스"""
    
    CHROME_BINARY_PATH = "/usr/bin/google-chrome"
    CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"

    def __init__(self, headless: bool = True):  # Lambda 환경에서는 기본적으로 headless 모드 사용
        self.headless = headless
        self.driver_path = self.CHROME_DRIVER_PATH
        self.setup_driver()

    def setup_driver(self):
        """드라이버 설정을 확인하는 메서드"""
        try:
            if not os.path.exists(self.CHROME_BINARY_PATH):
                raise FileNotFoundError(f"Chrome 바이너리를 찾을 수 없습니다: {self.CHROME_BINARY_PATH}")
            if not os.path.exists(self.CHROME_DRIVER_PATH):
                raise FileNotFoundError(f"ChromeDriver를 찾을 수 없습니다: {self.CHROME_DRIVER_PATH}")
            
            logger.info("Docker Lambda 환경의 크롬 드라이버 설정 확인 완료")
        except Exception as e:
            logger.error("크롬 드라이버 설정 확인 중 오류 발생", error=e)
            raise

    def get_driver(self):
        """설정된 크롬 드라이버를 반환하는 메서드"""
        try:
            options = Options()
            options.binary_location = self.CHROME_BINARY_PATH
            
            # Lambda 환경에 최적화된 옵션
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--window-size=1920x1080")
            
            # Lambda 환경 필수 옵션
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--single-process")
            options.add_argument("--no-zygote")
            
            # 성능 최적화 옵션
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-webgl")
            options.add_argument("--log-level=3")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-background-networking")
            
            # 메모리 사용량 최적화
            options.add_argument("--disable-dev-tools")
            options.add_argument("--disable-logging")
            options.add_argument("--disable-in-process-stack-traces")
            options.add_argument("--disable-crash-reporter")
            options.add_argument("--disable-breakpad")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-sync")
            options.add_argument("--force-color-profile=srgb")
            options.add_argument("--metrics-recording-only")
            options.add_argument("--mute-audio")
            options.add_argument("--no-first-run")
            options.add_argument("--password-store=basic")
            options.add_argument("--use-mock-keychain")
            options.add_argument("--disable-features=site-per-process")

            service = Service(self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("Docker Lambda 환경의 크롬 드라이버 실행 완료")
            return driver
        except Exception as e:
            logger.error("크롬 드라이버 실행 중 오류 발생", error=e)
            raise 