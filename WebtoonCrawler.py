from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup as bs
from time import sleep
import re
import json

# WebDriverFactory를 인터페이스로 정의하여 확장성을 높임
class WebDriverFactory(ABC):
    @abstractmethod
    def create_driver(self) -> webdriver.Chrome:
        pass

class ChromeWebDriverFactory(WebDriverFactory):
    def __init__(self, chromedriver_path: str):
        self.chromedriver_path = chromedriver_path

    def create_driver(self) -> webdriver.Chrome:
        chrome_service = Service(self.chromedriver_path)
        chrome_options = Options()
        return webdriver.Chrome(service=chrome_service, options=chrome_options)

# WebtoonScraper 인터페이스 정의
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

# NaverWebtoonScraper 구현
class NaverWebtoonScraper(WebtoonScraper):
    PLATFORM_NAME = "naver"

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

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def get_urls(self) -> list:
        return self.NAVER_WEBTOON_URLS

    def open_page(self, url: str):
        self.driver.get(url)
        WebDriverWait(self.driver, 3).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    def get_webtoon_elements(self) -> list:
        return WebDriverWait(self.driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, self.ITEM_CLASS))
        )

    def scrape_webtoon_info(self, webtoon_element) -> dict:
        try:

            rating = WebDriverWait(webtoon_element, 1).until(
                EC.presence_of_element_located((By.CLASS_NAME, self.RATING_CLASS))
            ).text.strip()

            title_element = webtoon_element.find_element(By.CLASS_NAME, self.TITLE_AREA_CLASS)
            title_element.click()

            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, self.TITLE_AREA_CLASS)))
            soup = bs(self.driver.page_source, 'html.parser')

            title = soup.find('h2', {'class': 'EpisodeListInfo__title--mYLjC'}).text.strip()
            day_age = soup.find('div', {'class': 'ContentMetaInfo__meta_info--GbTg4'}).find('em', {'class': 'ContentMetaInfo__info_item--utGrf'}).text.strip()
            thumbnail_url = soup.find('div', {'class': 'Poster__thumbnail_area--gviWY'}).find('img')['src']
            story = soup.find('div', {'class': 'EpisodeListInfo__summary_wrap--ZWNW5'}).find('p').text.strip()

            # 작가 정보 추출
            author_elements = soup.find_all('span', {'class': 'ContentMetaInfo__category--WwrCp'})
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

            # 장르 추출
            genre_elements = soup.find('div', {'class': 'TagGroup__tag_group--uUJza'}).find_all('a', {'class': 'TagGroup__tag--xu0OH'})
            genres = [genre.text.strip().replace('#', '') for genre in genre_elements]

            # 고유 ID 추출 및 int 형식으로 저장
            url = self.driver.current_url
            id_match = re.search(r'titleId=(\d+)', url)
            unique_id = int(id_match.group(1)) if id_match else None

            # 회차 수 추출
            episode_count_element = soup.find('div', {'class': 'EpisodeListView__count--fTMc5'})
            episode_count = int(re.search(r'\d+', episode_count_element.text).group()) if episode_count_element else None

            # 웹툰 1화 보기 링크 추출 및 접두사 추가
            first_episode_link = soup.find('a', {'class': 'EpisodeListUser__item--Fjp4R EpisodeListUser__view--PaVFx'})['href']
            full_first_episode_link = f"https://comic.naver.com{first_episode_link}"

            rating = re.search(r'\d+\.\d+', rating).group(0)
            day_match = re.search(r'(월|화|수|목|금|토|일)|완결', day_age)
            day = day_match.group(0) if day_match else None

            age_rating_match = re.search(r'(전체연령가|\d+세)', day_age)
            age_rating = age_rating_match.group(0) if age_rating_match else None

            return {
                "id": 0,
                "unique_id": unique_id,  # 고유 ID를 int 형식으로 저장
                "title": title,
                "day": day,
                "rating": rating,
                "thumbnail_url": thumbnail_url,
                "story": story,
                "url": url,
                "age_rating": age_rating,
                "authors": authors,
                "genres": genres,
                "episode_count": episode_count,  # 회차 수 추가
                "first_episode_link": full_first_episode_link  # 1화 링크 (접두사 추가)
            }
        except TimeoutException:
            print("TimeoutException: Could not load webtoon page. Skipping...")
            return None
        finally:
            self.driver.back()
            sleep(0.5)


# KaKaoWebtoonScraper 구현
class KaKaoWebtoonScraper(WebtoonScraper):
    PLATFORM_NAME = "kakao"
    
    KAKAO_WEBTOON_URLS = [
        'https://webtoon.kakao.com/?tab=mon',
        'https://webtoon.kakao.com/?tab=tue',
        'https://webtoon.kakao.com/?tab=wed',
        'https://webtoon.kakao.com/?tab=thu',
        'https://webtoon.kakao.com/?tab=fri',
        'https://webtoon.kakao.com/?tab=sat',
        'https://webtoon.kakao.com/?tab=sun',
        'https://webtoon.kakao.com/?tab=complete'  # 완결 웹툰
    ]

    # 웹툰 목록 관련 상수
    BUTTON_CLASS = "relative px-10 py-0 px-12 rounded-8 text-[12px] relative h-30 flex-shrink-0 bg-white light:bg-black"
    WEBTOON_LIST_CONTAINER_CLASS = "flex flex-wrap gap-4 content-start"
    WEBTOON_ITEM_CLASS = "flex-grow-0 overflow-hidden flex-[calc((100%-12px)/4)]"
    WEBTOON_LINK_CLASS = ".w-full.h-full.relative.overflow-hidden.rounded-8.before\\:absolute.before\\:inset-0.before\\:bg-grey-01.before\\:-z-1"
    
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
            # div 요소를 먼저 찾고, 그 안의 첫 번째 버튼을 찾습니다.
            container_div = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".w-fit.flex.overflow-x-scroll.no-scrollbar.scrolling-touch.space-x-6"))
            )
            
            # div 내의 첫 번째 버튼을 찾습니다.
            button = container_div.find_element(By.TAG_NAME, "button")

            # JavaScript를 통해 클릭 시도
            self.driver.execute_script("arguments[0].click();", button)
            sleep(1)  # 버튼 클릭 후 로딩 대기

            # 웹툰 목록 컨테이너 확인 후, 웹툰 요소 추출
            container = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.flex-wrap.gap-4.content-start"))
            )

            # 올바르게 CSS 선택자 작성
            return container.find_elements(By.CSS_SELECTOR, ".flex-grow-0.overflow-hidden.flex-\\[calc\\(\\(100\\%\\-12px\\)\\/4\\)\\]")
        
        except TimeoutException:
            print("TimeoutException: Could not find or click button. Skipping...")
            return []

    def scrape_webtoon_info(self, webtoon_element) -> dict:
        """웹툰 정보 스크래핑을 위한 클릭과 정보 추출."""
        print("정보 추출 시작~")
        try:
            # CSS_SELECTOR로 클래스 이름을 이용해 요소 선택
            link_element = webtoon_element.find_element(By.CSS_SELECTOR, self.WEBTOON_LINK_CLASS)
            
            # href 속성 가져오기
            href = link_element.get_attribute("href")
            if href:
                # 상대 경로를 절대 경로로 변환
                base_url = "https://webtoon.kakao.com"
                full_url = base_url + href

                print(full_url)
                self.driver.get(href)

                # 페이지 로딩을 기다림
                WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".w-full.h-full.relative.overflow-hidden.rounded-8.before\\:absolute.before\\:inset-0.before\\:bg-grey-01.before\\:-z-1")))

                # 여기서부터 상세 페이지 정보를 추출
                # 추출할 데이터는 다음에 알려주신다고 하였으니 추후 추가합니다.

                # 가상 데이터 반환 (추후 수정 필요)
                return {
                    "id": 0,  # 실제 ID 대신 임시로 사용
                    "unique_id": None,  # 추후 고유 ID 추출
                    "title": "Sample Title",
                    "day": "월",
                    "rating": "9.9",
                    "thumbnail_url": "http://example.com/thumbnail.jpg",
                    "story": "Sample Story",
                    "url": self.driver.current_url,
                    "age_rating": "전체연령가",
                    "authors": [{"name": "Sample Author", "role": "Writer", "link": "/author_link"}],
                    "genres": ["Action", "Fantasy"],
                    "episode_count": 100,
                    "first_episode_link": "http://example.com/first_episode"
                }

        except TimeoutException:
            print("TimeoutException: Could not load webtoon page. Skipping...")
            return None
        finally:
            self.driver.back()
            sleep(0.5)



# Repository 인터페이스 정의
class WebtoonRepository(ABC):
    @abstractmethod
    def save(self, webtoon_data: dict):
        pass

    @abstractmethod
    def save_to_json(self, filename: str):
        pass

class JsonWebtoonRepository(WebtoonRepository):
    def __init__(self):
        self.webtoons = []
        self.webtoon_id = 0

    def save(self, webtoon_data: dict):
        if self._exists(webtoon_data["title"]):
            self._update_day(webtoon_data)
        else:
            webtoon_data["id"] = self.webtoon_id
            self.webtoons.append(webtoon_data)
            self.webtoon_id += 1

    def _exists(self, title: str) -> bool:
        return any(webtoon['title'] == title for webtoon in self.webtoons)

    def _update_day(self, webtoon_data: dict):
        for webtoon in self.webtoons:
            if webtoon['title'] == webtoon_data['title']:
                webtoon['day'] += ', ' + webtoon_data['day']
                break

    def save_to_json(self, filename: str):
        with open(f"{filename}.json", "w", encoding="utf-8") as output_file:
            json.dump(self.webtoons, output_file, ensure_ascii=False, indent=4)

# Crawler 클래스는 웹스크래퍼와 레포지토리에 의존
class WebtoonCrawler:
    def __init__(self, scraper: WebtoonScraper, repository: WebtoonRepository):
        self.scraper = scraper
        self.repository = repository

    def run(self):
        for url in self.scraper.get_urls():
            self.scraper.open_page(url)
            webtoon_elements = self.scraper.get_webtoon_elements()

            if not webtoon_elements:
                print("No webtoon elements found. Exiting...")
                continue
        
            webtoon_list_len = 3 #len(webtoon_elements)
            for i in range(webtoon_list_len):
                try:
                    print(f"Processing: {i + 1} / {webtoon_list_len}")

                    webtoon_elements = self.scraper.get_webtoon_elements()
                    webtoon_data = self.scraper.scrape_webtoon_info(webtoon_elements[i])

                    if webtoon_data:
                        self.repository.save(webtoon_data)
                except StaleElementReferenceException:
                    print(f"StaleElementReferenceException encountered on element {i + 1}. Retrying...")
                    continue

# Factory Method를 사용하는 메인 함수
def main():
    driver_factory = ChromeWebDriverFactory('C:/chromedriver-win64/chromedriver.exe')
    driver = driver_factory.create_driver()
    repository = JsonWebtoonRepository()

    scraper_type = 'kakao'  # 'kakao'를 입력하면 KaKaoWebtoonScraper를 사용할 수 있습니다.

    if scraper_type == 'naver':
        scraper = NaverWebtoonScraper(driver)
    elif scraper_type == 'kakao':
        scraper = KaKaoWebtoonScraper(driver)

    crawler = WebtoonCrawler(scraper, repository)

    try:
        crawler.run()
    finally:
        repository.save_to_json("webtoon_list")
        input("프로그램을 종료하려면 엔터를 누르세요...")
        driver.quit()

if __name__ == "__main__":
    main()
