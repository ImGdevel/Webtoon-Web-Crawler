import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Optional, Tuple
from selenium.webdriver.remote.webelement import WebElement
from models.webtoon import WebtoonDTO
from models.author import AuthorDTO
from models.serialization_status import SerializationStatus
from models.platform import Platform
from models.age_rating import AgeRating
from models.day_of_week import DayOfWeek
from logger import Logger
from .i_webtoon_scraper import IWebtoonScraper
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import json
from dataclasses import asdict

logger = Logger()

class NaverWebtoonScraper(IWebtoonScraper):
    """네이버 웹툰 정보를 크롤링하는 클래스"""

    PLATFORM_NAME = Platform.NAVER

    # CSS 클래스 변수
    TITLE_CLASS = "EpisodeListInfo__title--mYLjC"
    THUMBNAIL_CLASS = "Poster__thumbnail_area--gviWY"
    SUMMARY_CLASS = "EpisodeListInfo__summary_wrap--ZWNW5"
    EPISODE_COUNT_CLASS = "EpisodeListView__count--fTMc5"
    META_INFO_CLASS = "ContentMetaInfo__meta_info--GbTg4"
    META_INFO_ITEM_CLASS = "ContentMetaInfo__info_item--utGrf"
    AUTHOR_CLASS = "ContentMetaInfo__meta_info--GbTg4"
    TAG_GROUP_CLASS = "TagGroup__tag_group--uUJza"
    TAG_CLASS = "TagGroup__tag--xu0OH"
    EXPAND_BUTTON_CLASS = "EpisodeListInfo__button_fold--ZKgEw"
    ABSENCE_INFO_CLASS = "EpisodeListInfo__info_text--MO6kz"
    CATEGORY_CLASS = "ContentMetaInfo__category--WwrCp"
    WAITING_LOAD_PAGE = 3
    EPISODE_LIST_META_INFO_CLASS = "EpisodeListInfo__meta_info--GbTg4"

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, class_name: str) -> WebElement:
        """주어진 클래스 이름을 가진 요소가 로드될 때까지 대기하는 메서드"""
        return WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )

    def get_title(self) -> str:
        """웹툰 제목을 가져오는 메서드"""
        element = self.wait_for_element(self.TITLE_CLASS)
        title = element.text.strip()
        cleaned_title = re.sub(r'\n.*', '', title).strip()
        return cleaned_title

    def get_thumbnail_url(self) -> str:
        """웹툰 썸네일 URL을 가져오는 메서드"""
        element = self.wait_for_element(self.THUMBNAIL_CLASS)
        return element.find_element(By.TAG_NAME, 'img').get_attribute('src')

    def get_story(self) -> str:
        """웹툰 설명을 가져오는 메서드"""
        element = self.wait_for_element(self.SUMMARY_CLASS)
        return element.find_element(By.TAG_NAME, 'p').text.strip()

    def get_day_age(self) -> Optional[str]:
        """웹툰의 연령 등급을 가져오는 메서드"""
        element = self.wait_for_element(self.META_INFO_CLASS)
        text = element.find_element(By.CLASS_NAME, self.META_INFO_ITEM_CLASS).text.strip()
        age_match = re.search(r'(전체연령가|12세|15세|19세)', text)
        if age_match:
            age_rating_map = {
                "전체연령가": AgeRating.ALL,
                "12세": AgeRating.AGE_12,
                "15세": AgeRating.AGE_15,
                "19세": AgeRating.ADULT
            }
            return age_rating_map[age_match.group(1)].name
        return None

    def get_day(self) -> Optional[str]:
        day_age_text = self.wait_for_element(self.META_INFO_CLASS).find_element(By.CLASS_NAME, self.META_INFO_ITEM_CLASS).text.strip()
        day_match = re.search(r'(월|화|수|목|금|토|일)', day_age_text)
        if day_match:
            korean_day = day_match.group(1)
            day_of_week = DayOfWeek.from_korean(korean_day)
            return day_of_week.name if day_of_week else None
        return None

    def get_status(self) -> str:
        """연재 상태를 가져오는 메서드"""
        day_age_text = self.wait_for_element(self.META_INFO_CLASS).find_element(By.CLASS_NAME, self.META_INFO_ITEM_CLASS).text.strip()
        absence_elements = self.driver.find_elements(By.CLASS_NAME, self.ABSENCE_INFO_CLASS)
        for element in absence_elements:
            if element.text.strip() == '휴재':
                return SerializationStatus.HIATUS.name
        
        if '완결' in day_age_text:
            return SerializationStatus.COMPLETED.name
        return SerializationStatus.ONGOING.name

    def get_genres(self) -> List[str]:
        """장르 정보를 가져오는 메서드"""
        try:
            expand_button = self.driver.find_element(By.CLASS_NAME, self.EXPAND_BUTTON_CLASS)
            if expand_button.is_displayed():
                expand_button.click()
        except Exception:
            logger.log("debug", "장르 카테고리 펼치기 버튼이 없거나 클릭할 수 없습니다.")

        WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, self.TAG_CLASS))
        )

        genre_elements = self.wait_for_element(self.TAG_GROUP_CLASS).find_elements(By.CLASS_NAME, self.TAG_CLASS)
        genres = [genre.text.strip().replace('#', '') for genre in genre_elements if genre.text.strip()]
        logger.log("debug", f"수집된 장르: {genres}")

        return genres

    def get_authors(self) -> List[AuthorDTO]:
        """저자 정보를 가져오는 메서드"""
        authors = []
        author_elements = self.driver.find_elements(By.CLASS_NAME, self.AUTHOR_CLASS)

        for element in author_elements:
            category_elements = element.find_elements(By.CLASS_NAME, self.CATEGORY_CLASS)
            
            for category in category_elements:
                link_tag = category.find_element(By.TAG_NAME, 'a')
                href = link_tag.get_attribute('href')
                name = link_tag.text.strip()

                if "artistTitle" in href:
                    author_id_match = re.search(r'id=(\d+)', href)
                    author_id = author_id_match.group(1) if author_id_match else None
                    url = href
                elif "community" in href:
                    author_id_match = re.search(r'u/([^?]+)', href)
                    author_id = author_id_match.group(1) if author_id_match else None
                    url = href.split('?')[0]  
                else:
                    logger.log("warning", f"알 수 없는 구조의 링크: {href}")
                    continue 

                role = category.text.split()[-1].strip()

                authors.append(AuthorDTO(author_id, name, role, url))
                logger.log("debug", f"저자 추가: {name}, ID: {author_id}, 역할: {role}, 링크: {url}") 

        return authors

    def get_unique_id(self) -> Optional[str]:
        """웹툰의 고유 ID를 가져오는 메서드"""
        url = self.driver.current_url
        id_match = re.search(r'titleId=(\d+)', url)
        return int(id_match.group(1)) if str(id_match) else None

    def get_episode_count(self) -> Optional[int]:
        """웹툰의 에피소드 수를 가져오는 메서드"""
        element = self.wait_for_element(self.EPISODE_COUNT_CLASS)
        return int(re.search(r'\d+', element.text).group()) if element else None

    def get_publish_start_date(self) -> Optional[str]:
        """웹툰의 시작 날짜를 가져오는 메서드"""
        try:
            current_url = self.driver.current_url
            modified_url = f"{current_url}&page=1&sort=ASC"
            self.driver.get(modified_url)

            first_item = self.wait_for_element("EpisodeListList__item--M8zq4")
            date_element = first_item.find_element(By.CLASS_NAME, "date")
            first_day = date_element.text.strip()

            return self.format_date(first_day)
        except Exception as e:
            logger.log("warning", f"시작일 추출 오류: {e}")
            return None

    def get_last_updated_date(self) -> Optional[str]:
        """웹툰의 마지막 업데이트 날짜를 가져오는 메서드"""
        try:
            first_item = self.wait_for_element("EpisodeListList__item--M8zq4")
            date_element = first_item.find_element(By.CLASS_NAME, "date")
            last_day = date_element.text.strip()
            return self.format_date(last_day)
        except Exception as e:
            logger.log("warning", f"마지막일 추출 오류: {e}")
            return None

    def format_date(self, date_str: str) -> str:
        return datetime.strptime(date_str, "%y.%m.%d").date().isoformat()

    def get_age_rating(self) -> Optional[str]:
        age_rating = self.get_day_age()
        return age_rating

    def get_serialization_status(self) -> str:
        return self.get_status()

    def fetch_webtoon(self, url: str) -> Tuple[bool, Optional[WebtoonDTO]]:
        """웹툰 정보를 가져와 WebtoonDTO 객체로 반환"""
        try:
            logger.log("info", f"웹툰 페이지 접속: {url}")
            self.driver.get(url)

            if "nid.naver.com" in self.driver.current_url:
                logger.log("warning", f"성인 인증이 필요한 웹툰입니다: {url}")
                return False, None

            title = self.get_title()
            external_id = self.get_unique_id()
            thumbnail_url = self.get_thumbnail_url()
            description = self.get_story()
            day_of_week = self.get_day()
            episode_count = self.get_episode_count()
            genres = self.get_genres()
            authors = self.get_authors()
            age_rating = self.get_age_rating()
            serialization_status = self.get_serialization_status()
            last_updated_date = self.get_last_updated_date()
            publish_start_date = self.get_publish_start_date()

            if title and external_id and thumbnail_url:
                webtoon_data = WebtoonDTO(
                    title=title,
                    external_id=external_id,
                    platform=self.PLATFORM_NAME.name,
                    day_of_week=day_of_week,
                    thumbnail_url=thumbnail_url,
                    link=url,
                    age_rating=age_rating,
                    description=description,
                    serialization_status=serialization_status,
                    episode_count=episode_count,
                    platform_rating=0.0,
                    publish_start_date=publish_start_date,
                    last_updated_date=last_updated_date,
                    authors=authors,
                    genres=genres
                )
                return True, webtoon_data
            else:
                logger.log("warning", "필수 정보를 찾을 수 없습니다.")
                return False, None
        except TimeoutException:
            if "nid.naver.com" in self.driver.current_url:
                logger.log("warning", f"성인 인증이 필요한 웹툰입니다 (Timeout 발생): {url}")
                return False, None
            logger.log("error", f"크롤링 오류 (TimeoutException): {url}")
            return False, None
        except Exception as e:
            logger.log("error", f"크롤링 오류: {e}")
            return False, None