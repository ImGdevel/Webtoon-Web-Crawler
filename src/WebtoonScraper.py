from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs
from datetime import datetime
from time import sleep
import re
from enum import Enum

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


class SerializationStatus(Enum):
    ONGOING = "ONGOING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

class AgeRating(Enum):
    ALL = "ALL"
    AGE_12 = "AGE_12"
    AGE_15 = "AGE_15"
    AGE_19 = "AGE_19"

class NaverWebtoonScraper(WebtoonScraper):
    PLATFORM_NAME = "NAVER"

    NAVER_WEBTOON_URLS = [
        'https://comic.naver.com/webtoon?tab=mon',
        'https://comic.naver.com/webtoon?tab=tue',
        'https://comic.naver.com/webtoon?tab=wed',
        'https://comic.naver.com/webtoon?tab=thu',
        'https://comic.naver.com/webtoon?tab=fri',
        'https://comic.naver.com/webtoon?tab=sat',
        'https://comic.naver.com/webtoon?tab=sun',
        'https://comic.naver.com/webtoon?tab=dailyPlus',
        'https://comic.naver.com/webtoon?tab=finish'
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

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.failed_webtoons = []

    def get_urls(self) -> list:
        return self.NAVER_WEBTOON_URLS

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # 특정 URL에서만 스크롤 기능을 사용
        if 'tab=finish' in url:
            self.scroll_to_load_all_content()

    def scroll_to_load_content(self, count):
        # 현재 페이지의 스크롤 높이 저장
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        for _ in range(int(count)):
            # 페이지를 아래로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)  # 로딩 시간을 대기

            # 새로운 스크롤 높이 저장
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # 스크롤 높이가 변하지 않으면 루프 종료
            if new_height == last_height:
                break

            last_height = new_height

    def scroll_to_load_all_content(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1.5)  # 로딩 시간 대기

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height

    def get_webtoon_elements(self) -> list:
        return WebDriverWait(self.driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, self.ITEM_CLASS))
        )

    def scrape_webtoon_info(self, webtoon_element) -> dict:
        try:
            rating = self.get_rating(webtoon_element)
            title = self.get_title(webtoon_element)
            soup = self.load_webtoon_page(webtoon_element)

            day_age = self.get_day_age(soup)
            thumbnail_url = self.get_thumbnail_url(soup)
            story = self.get_story(soup)
            authors = self.get_authors(soup)
            genres = self.get_genres(soup)
            unique_id = self.get_unique_id()
            episode_count = self.get_episode_count(soup)
            full_first_episode_link = self.get_first_episode_link(soup)
            last_update_day = self.get_last_update_day(soup)

            return {
                "id": 0,
                "uniqueId": unique_id,
                "platform": self.PLATFORM_NAME,
                "title": title,
                "day": self.get_day(day_age),
                "status": self.get_status(day_age, soup),
                "rating": rating,
                "thumbnailUrl": thumbnail_url,
                "story": story,
                "url": self.driver.current_url,
                "ageRating": self.get_age_rating(day_age),
                "authors": authors,
                "genres": genres,
                "episodeCount": episode_count,
                "firstEpisodeLink": full_first_episode_link,
                "firstDay": self.get_first_day(soup),
                "lastUpdateDay": last_update_day,
            }
        except TimeoutException:
            print("TimeoutException: Could not load webtoon page. Skipping...")
            self.failed_webtoons.append(webtoon_element)
            return None
        finally:
            self.go_back()

    def get_failed_webtoons(self) -> list:
        return self.failed_webtoons

    def get_rating(self, webtoon_element):
        # 등급 정보를 가져옴
        rating_text = WebDriverWait(webtoon_element, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, self.RATING_CLASS))
        ).text.strip()
        
        # "별점\n" 부분 제거하고 숫자만 반환 후 float로 변환
        return float(rating_text.replace("별점\n", "").strip())

    def get_title(self, webtoon_element):
        # 제목 정보를 가져옴
        title = WebDriverWait(webtoon_element, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_CLASS))
        ).text.strip()
        title_element = webtoon_element.find_element(By.CLASS_NAME, self.TITLE_AREA_CLASS)
        title_element.click()
        return title

    def load_webtoon_page(self, webtoon_element):
        # 페이지가 로드될 때까지 대기
        WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_AREA_CLASS))
        )
        return bs(self.driver.page_source, 'html.parser')

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
            return SerializationStatus.PAUSED.value
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


class KaKaoWebtoonScraper(WebtoonScraper):
    PLATFORM_NAME = "kakao"
    
    KAKAO_WEBTOON_URLS = [
        #'https://webtoon.kakao.com/?tab=mon',
        #'https://webtoon.kakao.com/?tab=tue',
        #'https://webtoon.kakao.com/?tab=wed',
        #'https://webtoon.kakao.com/?tab=thu',
        #'https://webtoon.kakao.com/?tab=fri',
        #'https://webtoon.kakao.com/?tab=sat',
        'https://webtoon.kakao.com/?tab=sun',
        #'https://webtoon.kakao.com/?tab=complete'
    ]

    # 웹툰 목록 관련 상수
    WEBTOON_LINK_CLASS = ".w-full.h-full.relative.overflow-hidden.rounded-8.before\\:absolute.before\\:inset-0.before\\:bg-grey-01.before\\:-z-1"
    CONTAINER_DIV_SELECTOR = ".w-fit.flex.overflow-x-scroll.no-scrollbar.scrolling-touch.space-x-6"
    WEBTOON_CONTAINER_SELECTOR = ".flex.flex-wrap.gap-4.content-start"
    WEBTOON_ELEMENT_SELECTOR = ".flex-grow-0.overflow-hidden.flex-\\[calc\\(\\(100\\%\\-12px\\)\\/4\\)\\]"
    TITLE_SELECTOR_X = '.whitespace-pre-wrap.break-all.break-words.support-break-word.overflow-hidden.text-ellipsis.s22-semibold-white.text-center.leading-26'

    TITLE_SELECTOR = 'whitespace-pre-wrap break-all break-words support-break-word overflow-hidden text-ellipsis !whitespace-nowrap s22-semibold-white text-center leading-26'
    STORY_SELECTOR = 'whitespace-pre-wrap break-all break-words support-break-word s13-regular-white leading-20 overflow-hidden'
    DAY_SELECTOR = 'whitespace-pre-wrap break-all break-words support-break-word font-badge !whitespace-nowrap rounded-5 s10-bold-black bg-white px-5 !text-[11px]'

    GENRE_SELECTOR = 'whitespace-pre-wrap break-all break-words support-break-word overflow-hidden text-ellipsis !whitespace-nowrap s14-medium-white'
    EPISODE_COUNT_SELECTOR = 'whitespace-pre-wrap break-all break-words support-break-word overflow-hidden text-ellipsis !whitespace-nowrap leading-14 s12-regular-white'
    FIRST_EPISODE_LINK_SELECTOR = 'relative px-10 py-0 w-full h-44 rounded-6 bg-white/10 mb-8'
    AUTHORS_SELECTOR = 'div.rounded-12.p-18.bg-white\\10.mb-8 > dl > div.flex.mb-8'

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_urls(self) -> list:
        return self.KAKAO_WEBTOON_URLS

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_webtoon_elements(self) -> list:
        """웹툰 목록을 클릭 후, 웹툰 요소를 추출합니다."""
        try:
            # 전체 버튼 클릭
            container_div = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.CONTAINER_DIV_SELECTOR))
            )
            button = container_div.find_element(By.TAG_NAME, "button")
            self.driver.execute_script("arguments[0].click();", button)

            # 웹툰 목록 컨테이너 확인 후, 웹툰 요소 추출
            container = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.WEBTOON_CONTAINER_SELECTOR))
            )
            return container.find_elements(By.CSS_SELECTOR, self.WEBTOON_ELEMENT_SELECTOR)
        
        except TimeoutException:
            print("TimeoutException: Could not find or click button. Skipping...")
            return []

    def scrape_webtoon_info(self, webtoon_element) -> dict:
        try:
            link_element = webtoon_element.find_element(By.CSS_SELECTOR, self.WEBTOON_LINK_CLASS)
            url = link_element.get_attribute("href")
            deapth_count = 0
            
            if url:
                self.driver.get(url)
                deapth_count = 1
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.TITLE_SELECTOR_X))
                )
                soup = bs(self.driver.page_source, 'html.parser')

                title = soup.find('p', {'class': self.TITLE_SELECTOR}).text.strip()

                episode_count = soup.find('p', {'class': self.EPISODE_COUNT_SELECTOR}).text.strip()

                id_match = re.search(r'titleId=(\d+)', url)
                unique_id = int(id_match.group(1)) if id_match else None

                # 정보탭에서 데이터 추출
                info_url = url + "?tab=profile"
                self.driver.get(info_url)
                deapth_count = 2
                soup = bs(self.driver.page_source, 'html.parser')
                WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.TITLE_SELECTOR_X))
                )

                story = soup.find('p', {'class': self.STORY_SELECTOR}).text.strip()
                day = soup.find('p', {'class': self.DAY_SELECTOR}).text.strip()

                # 장르 추출
                genre_elements = soup.find_all('p', {'class': self.GENRE_SELECTOR})
                genres = [genre.text.strip().replace('#', '') for genre in genre_elements]

                # 작가 정보 추출
                author_elements = soup.select('div.flex.mb-8')
                authors = []
                for element in author_elements:
                    role = element.find('dt').text.strip()
                    names = element.find('dd').text.strip().split(',')
                    for name in names:
                        authors.append({
                            "name": name.strip(),
                            "role": role,
                            "link": "/author_link"
                        })

                return {
                    "uniqueId": unique_id,
                    "title": title,
                    "day": day,
                    "rating": 0,
                    "thumbnailUrl": "http://example.com/thumbnail.jpg",
                    "thumbnailUrl2": "http://example.com/thumbnail.jpg",
                    "story": story,
                    "url": url,
                    "ageRating": "전체연령가",
                    "authors": authors,
                    "genres": genres,
                    "episodeCount": episode_count,
                    "firstEpisodeLink": ""
                }

        except TimeoutException:
            print("TimeoutException: Could not load webtoon page. Skipping...")
            return None
        finally:
            for i in range(deapth_count):
                self.driver.back()
            sleep(0.5)

