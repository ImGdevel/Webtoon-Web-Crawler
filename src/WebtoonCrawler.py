import os
import time
import json
import re
from logger import Logger 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from selenium.webdriver.remote.webelement import WebElement

logger = Logger()

class ChromeWebDriverManager:
    """크롬 드라이버를 자동으로 관리하는 클래스"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver_path = None
        self.setup_driver()

    def setup_driver(self):
        """드라이버를 자동으로 다운로드하고 설정하는 메서드"""
        try:
            self.driver_path = ChromeDriverManager().install()
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
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        logger.log("info", "크롬 드라이버 실행 완료")
        return driver


@dataclass
class AuthorDTO:
    id: int
    name: str
    role: str
    link: str

@dataclass
class WebtoonDTO:
    """웹툰 정보를 저장하는 데이터 객체"""
    url: str
    title: str
    external_id: int
    platform: str
    day_of_week: Optional[str]
    thumbnail_url: str
    link: str
    age_rating: Optional[str]
    description: str
    serialization_status: Optional[str]
    episode_count: Optional[int]
    authors: List[AuthorDTO]
    genres: List[str]

    def to_dict(self):
        return asdict(self)

class SerializationStatus(Enum):
    ONGOING = "연재"
    COMPLETED = "완결"
    HIATUS = "휴재"

class WebtoonScraper:
    """웹툰 정보를 크롤링하는 클래스"""

    PLATFORM_NAME = "NAVER"

    TITLE_CLASS = "EpisodeListInfo__title--mYLjC"
    THUMBNAIL_CLASS = "Poster__thumbnail_area--gviWY"
    SUMMARY_CLASS = "EpisodeListInfo__summary_wrap--ZWNW5"
    EPISODE_COUNT_CLASS = "EpisodeListView__count--fTMc5"
    META_INFO_CLASS = "ContentMetaInfo__meta_info--GbTg4"
    META_INFO_ITEM_CLASS = "ContentMetaInfo__info_item--utGrf"
    AUTHOR_CLASS = "AuthorInfo__name--xHCVQ"
    TAG_GROUP_CLASS = "TagGroup__tag_group--uUJza"
    TAG_CLASS = "TagGroup__tag--xu0OH"
    WAITING_LOAD_PAGE = 5

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, class_name: str) -> WebElement:
        return WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )

    def get_title(self) -> str:
        element = self.wait_for_element(self.TITLE_CLASS)
        return element.text.strip()

    def get_thumbnail_url(self) -> str:
        element = self.wait_for_element(self.THUMBNAIL_CLASS)
        return element.find_element(By.TAG_NAME, 'img').get_attribute('src')

    def get_story(self) -> str:
        element = self.wait_for_element(self.SUMMARY_CLASS)
        return element.find_element(By.TAG_NAME, 'p').text.strip()

    def get_day_age(self) -> Optional[str]:
        element = self.wait_for_element(self.META_INFO_CLASS)
        text = element.find_element(By.CLASS_NAME, self.META_INFO_ITEM_CLASS).text.strip()
        age_match = re.search(r'(전체연령가|12세|15세|19세)', text)
        return age_match.group(1) if age_match else None

    def get_day(self, day_age: str) -> Optional[str]:
        day_match = re.search(r'(월|화|수|목|금|토|일)', day_age)
        return day_match.group(1) if day_match else None

    def get_status(self, day_age: str) -> str:
        absence_elements = self.driver.find_elements(By.CLASS_NAME, "EpisodeListInfo__info_text--MO6kz")
        for element in absence_elements:
            if element.text.strip() == '휴재':
                return SerializationStatus.HIATUS.value
        
        if '완결' in day_age:
            return SerializationStatus.COMPLETED.value
        return SerializationStatus.ONGOING.value

    def get_genres(self) -> List[str]:
        genre_elements = self.wait_for_element(self.TAG_GROUP_CLASS).find_elements(By.CLASS_NAME, self.TAG_CLASS)
        return [genre.text.strip().replace('#', '') for genre in genre_elements]

    def get_authors(self) -> List[AuthorDTO]:
        authors = []
        author_elements = self.driver.find_elements(By.CLASS_NAME, self.AUTHOR_CLASS)
        for element in author_elements:
            link_tag = element.find_element(By.TAG_NAME, 'a')
            author_id = int(re.search(r'id=(\d+)', link_tag.get_attribute('href')).group(1))
            name = link_tag.text.strip()
            role = element.text.split()[-1]
            link = link_tag.get_attribute('href')
            authors.append(AuthorDTO(author_id, name, role, link))
        return authors

    def get_unique_id(self) -> Optional[int]:
        url = self.driver.current_url
        id_match = re.search(r'titleId=(\d+)', url)
        return int(id_match.group(1)) if id_match else None

    def get_episode_count(self) -> Optional[int]:
        element = self.wait_for_element(self.EPISODE_COUNT_CLASS)
        return int(re.search(r'\d+', element.text).group()) if element else None

    def fetch_webtoon(self, url: str) -> Tuple[bool, Optional[WebtoonDTO]]:
        """웹툰 정보를 가져와 WebtoonDTO 객체로 반환"""
        try:
            logger.log("info", f"웹툰 페이지 접속: {url}")
            self.driver.get(url)
            
            title = self.get_title()
            external_id = self.get_unique_id()
            thumbnail_url = self.get_thumbnail_url()
            description = self.get_story()
            day_age_text = self.wait_for_element(self.META_INFO_CLASS).find_element(By.CLASS_NAME, self.META_INFO_ITEM_CLASS).text.strip()
            age_rating = self.get_day_age()
            day_of_week = self.get_day(day_age_text)
            serialization_status = self.get_status(day_age_text)
            episode_count = self.get_episode_count()
            genres = self.get_genres()
            authors = self.get_authors()

            if title and external_id and thumbnail_url:
                webtoon_data = WebtoonDTO(
                    url=url,
                    title=title,
                    external_id=external_id,
                    platform=self.PLATFORM_NAME,
                    day_of_week=day_of_week,
                    thumbnail_url=thumbnail_url,
                    link=url,
                    age_rating=age_rating,
                    description=description,
                    serialization_status=serialization_status,
                    episode_count=episode_count,
                    authors=authors,
                    genres=genres
                )
                return True, webtoon_data
            else:
                logger.log("warning", "필수 정보를 찾을 수 없습니다.")
                return False, None
        except Exception as e:
            logger.log("error", f"크롤링 오류: {e}")
            return False, None

class WebtoonCrawler:
    """웹툰 크롤러 클래스"""

    def __init__(self, urls: List[str]):
        self.urls = urls
        self.driver_manager = ChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraper(self.driver)
        self.success_list: List[dict] = []
        self.failure_list: List[dict] = []

    def run(self) -> None:
        """크롤링 실행 메서드"""
        for url in self.urls:
            success, webtoon_data = self.scraper.fetch_webtoon(url)
            if success and webtoon_data:
                self.success_list.append(webtoon_data.to_dict())
            else:
                self.failure_list.append({"url": url})

        self.save_results()
        self.driver.quit()

    def save_results(self):
        """크롤링 결과를 JSON 파일로 저장"""
        save_to_json(self.success_list, "webtoon_data.json")
        save_to_json(self.failure_list, "failed_webtoon_list.json")

def save_to_json(data_list: List[dict], filename: str) -> None:
    """크롤링된 데이터를 JSON 파일로 저장"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
        logger.log("info", f"데이터 저장 완료: {filename}")
    except Exception as e:
        logger.log("error", f"데이터 저장 실패: {e}")

if __name__ == "__main__":
    sample_urls = [
        "https://comic.naver.com/webtoon/list?titleId=747271",
        "https://comic.naver.com/webtoon/list?titleId=769209",
        "https://comic.naver.com/webtoon/list?titleId=776601",
    ]
    crawler = WebtoonCrawler(sample_urls)
    crawler.run()
