from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Type
from scrapers.platforms.naver_webtoon_scraper import NaverWebtoonScraper
from scrapers.webtoon_scraper_builder import WebtoonScraperBuilder
from scrapers.common import IWebtoonScraper

class WebtoonScraperFactory:
    """웹툰 스크래퍼 팩토리 클래스"""
    
    _scrapers: Dict[str, Type[IWebtoonScraper]] = {
        "naver": NaverWebtoonScraper
    }

    @classmethod
    def register_scraper(cls, platform: str, scraper_class: Type[IWebtoonScraper]) -> None:
        """새로운 스크래퍼를 등록하는 메서드"""
        cls._scrapers[platform] = scraper_class

    @classmethod
    def create_builder(cls, driver: WebDriver, platform: str = "naver") -> WebtoonScraperBuilder:
        """주어진 플랫폼에 맞는 스크래퍼 빌더를 생성"""
        if platform not in cls._scrapers:
            raise ValueError(f"지원하지 않는 플랫폼: {platform}")
        
        return WebtoonScraperBuilder(driver, cls._scrapers[platform])

    @classmethod
    def create_title_genre_scraper(cls, driver: WebDriver, platform: str = "naver") -> IWebtoonScraper:
        """제목과 장르만 수집하는 스크래퍼 생성"""
        return cls.create_builder(driver, platform).scrape_title().scrape_genres().build()

    @classmethod
    def create_basic_info_scraper(cls, driver: WebDriver, platform: str = "naver") -> IWebtoonScraper:
        """기본 정보를 수집하는 스크래퍼 생성"""
        return (cls.create_builder(driver, platform)
            .scrape_title()
            .scrape_thumbnail()
            .scrape_story()
            .scrape_genres()
            .scrape_authors()
            .build())

    @classmethod
    def create_full_info_scraper(cls, driver: WebDriver, platform: str = "naver") -> IWebtoonScraper:
        """모든 정보를 수집하는 스크래퍼 생성"""
        return (cls.create_builder(driver, platform)
            .scrape_title()
            .scrape_thumbnail()
            .scrape_story()
            .scrape_day_age()
            .scrape_day()
            .scrape_status()
            .scrape_genres()
            .scrape_authors()
            .scrape_unique_id()
            .scrape_episode_count()
            .scrape_dates()
            .build()) 
