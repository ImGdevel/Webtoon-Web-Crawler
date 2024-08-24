from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class WebDriverFactory(ABC):
    @abstractmethod
    def create_driver(self) -> webdriver.Chrome:
        pass

class ChromeWebDriverFactory(WebDriverFactory):
    def __init__(self, chromedriver_path: str):
        self.chromedriver_path = chromedriver_path

    def create_driver(self) -> webdriver.Chrome:
        chrome_service = Service(self.chromedriver_path)
        chrome_options = Options()
        return webdriver.Chrome(service=chrome_service, options=chrome_options)
