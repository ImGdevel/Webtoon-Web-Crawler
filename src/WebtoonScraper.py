import logging
import re
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from src.Model import WebtoonCreateRequestDTO, AuthorDTO, GenreDTO
from src.Model.enum import AgeRating, SerializationStatus

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class WebtoonScraper(ABC):
    """웹툰 스크래퍼 추상 클래스"""
    def __init__(self, driver):
        self.driver = driver

    @abstractmethod
    def scrape_webtoon_info(self, url) -> WebtoonCreateRequestDTO:
        """주어진 URL에서 웹툰 정보를 수집하는 메서드"""
        pass


class NaverWebtoonScraper(WebtoonScraper):
    """네이버 웹툰 크롤러"""

    PLATFORM_NAME = "NAVER"

    TITLE_CLASS = "ContentTitle__title--e3qXt"
    META_INFO_CLASS = "ContentMetaInfo__meta_info--GbTg4"
    META_INFO_ITEM_CLASS = "ContentMetaInfo__info_item--utGrf"
    THUMBNAIL_CLASS = "Poster__thumbnail_area--gviWY"
    SUMMARY_CLASS = "EpisodeListInfo__summary_wrap--ZWNW5"
    EPISODE_COUNT_CLASS = "EpisodeListView__count--fTMc5"
    TAG_GROUP_CLASS = "TagGroup__tag_group--uUJza"
    TAG_CLASS = "TagGroup__tag--xu0OH"
    EPISODE_LIST_META_INFO_CLASS = "EpisodeListList__meta_info--Cgquz"

    WATTING_LOAD_PAGE = 3

    def scrape_webtoon_info(self, url) -> WebtoonCreateRequestDTO:
        """웹툰 상세 페이지에서 정보를 수집하는 메서드"""
        try:
            logger.info(f"Opening webtoon page: {url}")
            self.driver.get(url)

            WebDriverWait(self.driver, self.WATTING_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_CLASS))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            title = self.get_title(soup)
            thumbnail_url = self.get_thumbnail_url(soup)
            story = self.get_story(soup)
            authors = self.get_authors(soup)
            genres = self.get_genres(soup)
            unique_id = self.get_unique_id(url)
            episode_count = self.get_episode_count(soup)
            last_update_day = self.get_last_update_day(soup)

            authors_list = [AuthorDTO(name=a['name'], role=a['role'], link=a['link']) for a in authors]
            genres_list = [GenreDTO(name=g) for g in genres]

            return WebtoonCreateRequestDTO(
                title=title,
                externalId=str(unique_id),
                platform=self.PLATFORM_NAME,
                thumbnailUrl=thumbnail_url,
                link=url,
                description=story,
                episodeCount=episode_count,
                lastUpdatedDate=last_update_day,
                authors=authors_list,
                genres=genres_list
            )

        except TimeoutException:
            logger.error(f"Timeout while opening page: {url}")
            return None
        except WebDriverException as e:
            logger.error(f"WebDriver error while scraping {url}: {e}")
            return None

    def get_title(self, soup):
        return soup.find('h2', {'class': self.TITLE_CLASS}).text.strip()

    def get_thumbnail_url(self, soup):
        return soup.find('div', {'class': self.THUMBNAIL_CLASS}).find('img')['src']

    def get_story(self, soup):
        return soup.find('div', {'class': self.SUMMARY_CLASS}).find('p').text.strip()

    def get_authors(self, soup):
        author_elements = soup.find_all('span', {'class': self.META_INFO_ITEM_CLASS})
        authors = []
        for author in author_elements:
            name = author.find('a').text.strip()
            link = author.find('a')['href']
            role = "Writer"
            authors.append({"name": name, "role": role, "link": link})
        return authors

    def get_genres(self, soup):
        genre_elements = soup.find('div', {'class': self.TAG_GROUP_CLASS}).find_all('a', {'class': self.TAG_CLASS})
        return [genre.text.strip().replace('#', '') for genre in genre_elements]

    def get_unique_id(self, url):
        id_match = re.search(r'titleId=(\d+)', url)
        return int(id_match.group(1)) if id_match else None

    def get_episode_count(self, soup):
        episode_count_element = soup.find('div', {'class': self.EPISODE_COUNT_CLASS})
        return int(re.search(r'\d+', episode_count_element.text).group()) if episode_count_element else None

    def get_last_update_day(self, soup):
        last_update_element = soup.find('div', {'class': self.EPISODE_LIST_META_INFO_CLASS}).find('span', {'class': 'date'})
        return datetime.strptime(last_update_element.text.strip(), "%y.%m.%d").date().isoformat() if last_update_element else None
