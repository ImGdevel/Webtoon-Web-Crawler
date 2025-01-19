from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup as bs
from datetime import datetime
from time import sleep
import re
from .WebtoonScraper import WebtoonScraper
from .enum import AgeRating, SerializationStatus

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

