import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup as bs
from datetime import datetime
from time import sleep
import re
from .WebtoonScraper import WebtoonScraper
from src.Model import WebtoonCreateRequestDTO, AuthorDTO, GenreDTO
from src.Model.enum import AgeRating, SerializationStatus

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class NaverWebtoonScraper(WebtoonScraper):
    PLATFORM_NAME = "NAVER"

    NAVER_WEBTOON_URLS = [
        'https://comic.naver.com/webtoon?tab=mon',
        #'https://comic.naver.com/webtoon?tab=tue',
        #'https://comic.naver.com/webtoon?tab=wed',
        #'https://comic.naver.com/webtoon?tab=thu',
        #'https://comic.naver.com/webtoon?tab=fri',
        #'https://comic.naver.com/webtoon?tab=sat',
        #'https://comic.naver.com/webtoon?tab=sun',
        #'https://comic.naver.com/webtoon?tab=dailyPlus',
        #'https://comic.naver.com/webtoon?tab=finish'
    ]
    
    CONTENT_LIST_CLASS = "ContentList__content_list--q5KXY"
    ITEM_CLASS = "item"
    RATING_CLASS = "Rating__star_area--dFzsb"
    TITLE_AREA_CLASS = "ContentTitle__title_area--x24vt"
    META_INFO_CLASS = 'ContentMetaInfo__meta_info--GbTg4'
    META_INFO_ITEM_CLASS = 'ContentMetaInfo__info_item--utGrf'
    THUMBNAIL_CLASS = 'Poster__thumbnail_area--gviWY'
    SUMMARY_CLASS = 'EpisodeListInfo__summary_wrap--ZWNW5'
    EPISODE_COUNT_CLASS = 'EpisodeListView__count--fTMc5'
    FIRST_EPISODE_LINK_CLASS = 'EpisodeListUser__item--Fjp4R EpisodeListUser__view--PaVFx'
    TITLE_CLASS = 'ContentTitle__title--e3qXt'
    AUTHOR_CLASS = 'ContentMetaInfo__category--WwrCp'
    TAG_GROUP_CLASS = 'TagGroup__tag_group--uUJza'
    TAG_CLASS = 'TagGroup__tag--xu0OH'
    EPISODE_LIST_INFO_CLASS = 'EpisodeListInfo__icon_hiatus--kbQXO'
    EPISODE_LIST_META_INFO_CLASS = 'EpisodeListList__meta_info--Cgquz'

    SCROLL_SLEEP_TIME = 0.5
    WATTING_LOAD_PAGE = 1

    def __init__(self, driver):
        logger.info("Initializing NaverWebtoonScraper")
        self.driver = driver
        self.failed_webtoons = []

    def get_urls(self):
        return self.NAVER_WEBTOON_URLS

    def open_page(self, url):
        try:
            logger.info(f"Opening page: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, self.WATTING_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_CLASS))
            )
            if 'tab=finish' in url:
                self._scroll_to_load_all_content()
        except TimeoutException:
            logger.error(f"Timeout while opening page: {url}")
            raise

    def _scroll_to_load_all_content(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(self.SCROLL_SLEEP_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("All content loaded")
                break
            last_height = new_height

    def get_webtoon_elements(self):
        try:
            return WebDriverWait(self.driver, self.WATTING_LOAD_PAGE).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, self.ITEM_CLASS))
            )
        except TimeoutException:
            logger.warning("Timeout while retrieving webtoon elements")
            return []

    def scrape_webtoon_info(self, webtoon_element) -> WebtoonCreateRequestDTO:
        try:
            rating = self.get_rating(webtoon_element)
            title = self.get_title(webtoon_element)
            soup = self.load_webtoon_page()

            day_age = self.get_day_age(soup)
            thumbnail_url = self.get_thumbnail_url(soup)
            story = self.get_story(soup)
            authors = self.get_authors(soup) 
            genres = self.get_genres(soup) 
            unique_id = self.get_unique_id()
            episode_count = self.get_episode_count(soup)
            last_update_day = self.get_last_update_day(soup)

            authors_list = [AuthorDTO(
                name=author['name'],
                role=author['role'],
                link=author['link']
            ) for author in authors]

            genres_list = [GenreDTO(
                name=genre
            ) for genre in genres]

            return WebtoonCreateRequestDTO(
                title=title,
                external_id=str(unique_id),
                platform=self.PLATFORM_NAME,
                day_of_week=self.get_day(day_age),
                thumbnail_url=thumbnail_url,
                link=self.driver.current_url,
                age_rating=self.get_age_rating(day_age),
                description=story,
                serialization_status=self.get_status(day_age, soup),
                episode_count=episode_count,
                platform_rating=rating,
                publish_start_date=self.get_first_day(soup),
                last_updated_date=last_update_day,
                authors=authors_list,
                genres=genres_list
            )
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Error scraping webtoon info: {e}")
            return None
        finally:
            self.go_back()


    def get_failed_webtoons(self) -> list:
        return self.failed_webtoons

    def get_rating(self, webtoon_element):
        rating_text = WebDriverWait(webtoon_element, self.WATTING_LOAD_PAGE).until(
            EC.presence_of_element_located((By.CLASS_NAME, self.RATING_CLASS))
        ).text.strip()
        
        return float(rating_text.replace("별점\n", "").strip())

    def get_title(self, webtoon_element):
        title = WebDriverWait(webtoon_element, self.WATTING_LOAD_PAGE).until(
            EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_CLASS))
        ).text.strip()
        title_element = webtoon_element.find_element(By.CLASS_NAME, self.TITLE_AREA_CLASS)
        title_element.click()
        return title

    def load_webtoon_page(self):
        try:
            logger.info("Loading webtoon page")
            WebDriverWait(self.driver, self.WATTING_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_AREA_CLASS))
            )
            return bs(self.driver.page_source, 'html.parser')
        except TimeoutException as e:
            logger.error(f"Timeout while loading webtoon page: {str(e)}")
            self.failed_webtoons.append(self.driver.current_url)
            raise
        except WebDriverException as e:
            logger.error(f"WebDriver exception while loading webtoon page: {str(e)}")
            self.failed_webtoons.append(self.driver.current_url)
            raise
        except Exception as e:
            logger.error(f"Unexpected error while loading webtoon page: {str(e)}") 
            self.failed_webtoons.append(self.driver.current_url)
            raise


    def get_day_age(self, soup):
        return soup.find('div', {'class': self.META_INFO_CLASS}).find('em', {'class': self.META_INFO_ITEM_CLASS}).text.strip()

    def get_thumbnail_url(self, soup):
        return soup.find('div', {'class': self.THUMBNAIL_CLASS}).find('img')['src']

    def get_story(self, soup):
        return soup.find('div', {'class': self.SUMMARY_CLASS}).find('p').text.strip()

    def get_authors(self, soup):
        author_elements = soup.find_all('span', {'class': self.AUTHOR_CLASS})
        authors = []
        for author_element in author_elements:
            author_name = author_element.find('a').text.strip()
            author_role = author_element.find(text=True, recursive=False).strip().replace("::after", "").replace(".", "")
            author_link = author_element.find('a')['href']
            authors.append({
                "name": author_name,
                "role": author_role,
                "link": author_link
            })
        return authors

    def get_genres(self, soup):
        genre_elements = soup.find('div', {'class': self.TAG_GROUP_CLASS}).find_all('a', {'class': self.TAG_CLASS})
        return [genre.text.strip().replace('#', '') for genre in genre_elements]

    def get_unique_id(self):
        url = self.driver.current_url
        id_match = re.search(r'titleId=(\d+)', url)
        return int(id_match.group(1)) if id_match else None

    def get_episode_count(self, soup):
        episode_count_element = soup.find('div', {'class': self.EPISODE_COUNT_CLASS})
        return int(re.search(r'\d+', episode_count_element.text).group()) if episode_count_element else None

    def get_first_episode_link(self, soup):
        first_episode_link = soup.find('a', {'class': self.FIRST_EPISODE_LINK_CLASS})['href']
        return f"https://comic.naver.com{first_episode_link}"

    def get_day(self, day_age):
        day_match = re.search(r'(월|화|수|목|금|토|일)', day_age)
        return day_match.group(0) if day_match else None

    def get_status(self, day_age, soup):
        absence = soup.find('i', {'class': self.EPISODE_LIST_INFO_CLASS})
        if absence and absence.text == '휴재':
            return SerializationStatus.HIATUS.value
        day_match = re.search(r'\b완결\b', day_age)
        return SerializationStatus.COMPLETED.value if day_match else SerializationStatus.ONGOING.value

    def get_age_rating(self, day_age):
        age_rating_match = re.search(r'(전체연령가|12세|15세|19세)', day_age)
        if age_rating_match:
            if age_rating_match.group(1) == '전체연령가':
                return AgeRating.ALL.value
            elif age_rating_match.group(1) == '12세':
                return AgeRating.AGE_12.value
            elif age_rating_match.group(1) == '15세':
                return AgeRating.AGE_15.value
            elif age_rating_match.group(1) == '19세':
                return AgeRating.AGE_19.value
        return None

    def get_first_day(self, soup):
        first_day = soup.find('div', {'class': self.EPISODE_LIST_META_INFO_CLASS}).find('span', {'class': 'date'}).text.strip()
        return datetime.strptime(first_day, "%y.%m.%d").isoformat()

    
    def get_last_update_day(self, soup):
        last_update_element = soup.find('div', {'class': self.EPISODE_LIST_META_INFO_CLASS}).find('span', {'class': 'date'})
        if last_update_element:
            last_update_str = last_update_element.text.strip()
            return datetime.strptime(last_update_str, "%y.%m.%d").date().isoformat()  

    def go_back(self):
        for _ in range(1):
            self.driver.back()
        sleep(0.01)
