from typing import List, Optional, Type
from .naver_webtoon_scraper import NaverWebtoonScraper
from selenium.webdriver.remote.webdriver import WebDriver
from .i_webtoon_scraper import IWebtoonScraper

class WebtoonScraperBuilder:
    def __init__(self, driver: WebDriver, scraper_class: Type[IWebtoonScraper]):
        self.driver = driver
        self.scraper_class = scraper_class
        self._scrape_title = False
        self._scrape_thumbnail = False
        self._scrape_story = False
        self._scrape_day_age = False
        self._scrape_day = False
        self._scrape_status = False
        self._scrape_genres = False
        self._scrape_authors = False
        self._scrape_unique_id = False
        self._scrape_episode_count = False
        self._scrape_dates = False

    def scrape_title(self) -> 'WebtoonScraperBuilder':
        self._scrape_title = True
        return self

    def scrape_thumbnail(self) -> 'WebtoonScraperBuilder':
        self._scrape_thumbnail = True
        return self

    def scrape_story(self) -> 'WebtoonScraperBuilder':
        self._scrape_story = True
        return self

    def scrape_day_age(self) -> 'WebtoonScraperBuilder':
        self._scrape_day_age = True
        return self

    def scrape_day(self) -> 'WebtoonScraperBuilder':
        self._scrape_day = True
        return self

    def scrape_status(self) -> 'WebtoonScraperBuilder':
        self._scrape_status = True
        return self

    def scrape_genres(self) -> 'WebtoonScraperBuilder':
        self._scrape_genres = True
        return self

    def scrape_authors(self) -> 'WebtoonScraperBuilder':
        self._scrape_authors = True
        return self

    def scrape_unique_id(self) -> 'WebtoonScraperBuilder':
        self._scrape_unique_id = True
        return self

    def scrape_episode_count(self) -> 'WebtoonScraperBuilder':
        self._scrape_episode_count = True
        return self

    def scrape_dates(self) -> 'WebtoonScraperBuilder':
        self._scrape_dates = True
        return self

    def build(self) -> IWebtoonScraper:
        scraper = self.scraper_class(self.driver)
        scraper.scrape_title = self._scrape_title
        scraper.scrape_thumbnail = self._scrape_thumbnail
        scraper.scrape_story = self._scrape_story
        scraper.scrape_day_age = self._scrape_day_age
        scraper.scrape_day = self._scrape_day
        scraper.scrape_status = self._scrape_status
        scraper.scrape_genres = self._scrape_genres
        scraper.scrape_authors = self._scrape_authors
        scraper.scrape_unique_id = self._scrape_unique_id
        scraper.scrape_episode_count = self._scrape_episode_count
        scraper.scrape_dates = self._scrape_dates
        return scraper

    @classmethod
    def create_title_genre_scraper(cls, driver: WebDriver) -> 'WebtoonScraperBuilder':
        return cls(driver, NaverWebtoonScraper).scrape_title().scrape_genres()

    @classmethod
    def create_basic_info_scraper(cls, driver: WebDriver) -> 'WebtoonScraperBuilder':
        return (cls(driver, NaverWebtoonScraper)
            .scrape_title()
            .scrape_thumbnail()
            .scrape_story()
            .scrape_genres()
            .scrape_authors()) 