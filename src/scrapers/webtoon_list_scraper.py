from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from logger import Logger

logger = Logger()

class WebtoonListScraper:
    """웹툰 리스트 페이지에서 웹툰 URL을 수집하는 스크래퍼"""

    WAITING_LOAD_PAGE = 5

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
        """웹툰 리스트 페이지에서 웹툰 URL들을 추출한다."""
        webtoon_urls = []

        try:
            logger.log("info", f"페이지 열기: {url}")
            self.driver.get(url)

            # 페이지 전체가 로드될 때까지 기다림
            WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ContentList__content_list--q5KXY"))
            )

            # `li.item`이 로드될 때까지 대기
            webtoon_elements = WebDriverWait(self.driver, self.WAITING_LOAD_PAGE).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
            )

            for element in webtoon_elements:
                try:
                    # `li.item` 내부의 `a.Poster_link--sopnC`를 XPath로 찾음
                    link_element = WebDriverWait(element, self.WAITING_LOAD_PAGE).until(
                        EC.presence_of_element_located((By.XPATH, ".//a[contains(@class, 'Poster__link--sopnC')]"))
                    )

                    relative_url = link_element.get_attribute("href")

                    if relative_url and "/webtoon/list" in relative_url:
                        full_url = self.remove_tab_param(f"https://comic.naver.com{relative_url}" if relative_url.startswith("/") else relative_url)
                        webtoon_urls.append(full_url)

                except (TimeoutException, NoSuchElementException):
                    logger.log("warning", "웹툰 링크 요소를 찾을 수 없음")
                except Exception as e:
                    logger.log("error", f"웹툰 URL 추출 오류: {e}")

            logger.log("info", f"총 {len(webtoon_urls)}개의 웹툰 URL을 수집함")

        except TimeoutException:
            logger.log("error", f"페이지 로딩 실패: {url}")

        return webtoon_urls
