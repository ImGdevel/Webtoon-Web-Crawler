from selenium import webdriver
from .naver_webtoon_scraper import NaverWebtoonScraper  

class WebtoonScraperFactory:
    """네이버 웹툰 스크래퍼 팩토리 클래스"""

    @staticmethod
    def create_scraper(driver: webdriver.Chrome, scraper_type: str) -> NaverWebtoonScraper:
        """주어진 드라이버와 스크래퍼 종류에 따라 NaverWebtoonScraper 인스턴스를 생성"""
        if scraper_type == "naver":
            return NaverWebtoonScraper(driver)
        else:
            raise ValueError(f"Unknown scraper type: {scraper_type}") 