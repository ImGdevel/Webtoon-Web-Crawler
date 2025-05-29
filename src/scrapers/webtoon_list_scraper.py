from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from utils.logger import logger
from time import sleep

class WebtoonListScraper:
    """웹툰 리스트 페이지에서 웹툰 URL을 수집하는 스크래퍼"""

    WAITING_LOAD_PAGE = 5
    SCROLL_SLEEP_TIME = 2 
    SCROLL_LIMIT = 30

    def __init__(self, driver):
        self.driver = driver

    def remove_tab_param(self, url: str) -> str:
        """URL에서 'tab' 파라미터를 제거하는 함수"""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'tab' in query_params:
            del query_params['tab']
        new_query = urlencode(query_params, doseq=True)
        new_url = parsed_url._replace(query=new_query)
        return urlunparse(new_url)

    def get_webtoon_urls(self, url: str) -> list:
        """웹툰 리스트 페이지에서 중복 없이 웹툰 URL들을 추출한다."""
        webtoon_urls = set()

        try:
            logger.log("info", f"페이지 열기: {url}")
            self.driver.get(url)

            WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ContentList__content_list--q5KXY"))
            )

            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0

            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(self.SCROLL_SLEEP_TIME)

                webtoon_elements = self.driver.find_elements(By.CLASS_NAME, "item")
                previous_count = len(webtoon_urls)

                for element in webtoon_elements:
                    try:
                        link_element = element.find_element(By.XPATH, ".//a[contains(@class, 'Poster__link--sopnC')]")
                        relative_url = link_element.get_attribute("href")
                        if relative_url and "/webtoon/list" in relative_url:
                            full_url = self.remove_tab_param(f"https://comic.naver.com{relative_url}" if relative_url.startswith("/") else relative_url)
                            webtoon_urls.add(full_url)
                    except Exception as e:
                        logger.log("warning", f"웹툰 링크 추출 오류: {e}")

                if len(webtoon_urls) == previous_count:
                    logger.log("info", "더 이상 새로운 웹툰 없음, 종료")
                    break

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.log("info", "마지막 페이지 도달")
                    break

                last_height = new_height
                scroll_count += 1
                if scroll_count >= self.SCROLL_LIMIT:
                    logger.log("info", "스크롤 제한에 도달, 종료")
                    break

            logger.log("info", f"총 {len(webtoon_urls)}개의 웹툰 URL을 수집함")

        except Exception as e:
            logger.log("error", f"웹툰 리스트 수집 오류: {e}")

        return list(webtoon_urls)