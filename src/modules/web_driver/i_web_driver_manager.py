from abc import ABC, abstractmethod

class IWebDriverManager(ABC):
    @abstractmethod
    def setup_driver(self):
        """드라이버를 설정하는 메서드"""
        pass

    @abstractmethod
    def get_driver(self):
        """설정된 드라이버를 반환하는 메서드"""
        pass 