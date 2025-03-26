from abc import ABC, abstractmethod

# WebtoonScraper 인터페이스
class WebtoonScraper(ABC):
    @abstractmethod
    def get_urls(self) -> list:
        pass

    @abstractmethod
    def open_page(self, url: str):
        pass

    @abstractmethod
    def get_webtoon_elements(self) -> list:
        pass

    @abstractmethod
    def scrape_webtoon_info(self, webtoon_element) -> dict:
        pass
