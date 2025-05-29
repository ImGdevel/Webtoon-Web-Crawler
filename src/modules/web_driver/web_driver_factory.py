from typing import Optional
from .driver.lambda_chrome_webdriver_manager import ChromeWebDriverManager
from .driver.local_chrome_webdriver_manager import LocalChromeWebDriverManager
from .common.i_web_driver_manager import IWebDriverManager

class WebDriverFactory:
    """WebDriver 인스턴스를 생성하는 팩토리 클래스"""
    
    @staticmethod
    def create_driver(environment: str = "local", headless: bool = False) -> IWebDriverManager:
        """
        환경에 맞는 WebDriver 인스턴스를 생성합니다.
        
        Args:
            environment (str): 실행 환경 ("local" 또는 "lambda")
            headless (bool): 헤드리스 모드 사용 여부
            
        Returns:
            IWebDriverManager: WebDriver 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 환경이 지정된 경우
        """
        if environment.lower() == "local":
            return LocalChromeWebDriverManager(headless=headless)
        elif environment.lower() == "lambda":
            return ChromeWebDriverManager(headless=headless)
        else:
            raise ValueError(f"지원하지 않는 환경입니다: {environment}") 