from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver

class WebDriverManager(ABC):
    """WebDriver 매니저의 기본 인터페이스"""
    
    @abstractmethod
    def get_driver(self) -> WebDriver:
        """WebDriver 인스턴스를 생성하고 반환합니다."""
        pass 