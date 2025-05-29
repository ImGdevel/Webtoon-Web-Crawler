import atexit
from typing import List, Optional, Tuple
from utils.logger import logger
from modules.web_driver import IWebDriverManager, WebDriverFactory
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory
from crawler import IWebtoonCrawler
from crawler.batch.batch_processor import BatchProcessor
from selenium.webdriver.remote.webdriver import WebDriver

class InitWebtoonCrawler(IWebtoonCrawler):
    """웹툰 초기화 크롤러 클래스"""

    def __init__(
        self,
        driver_manager: Optional[IWebDriverManager] = None,
        batch_size: int = 10
    ):
        self.driver_manager = driver_manager or WebDriverFactory.create_driver(headless=True)
        self.driver: WebDriver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraperFactory.create_basic_info_scraper(self.driver, platform="naver")
        self.batch_processor = BatchProcessor(batch_size)
        self.urls: List[str] = []
        self.current_batch_results: Tuple[List[dict], List[dict]] = ([], [])
        self.is_running: bool = False

    def initialize(self, url_list: List[str]) -> None:
        """URL 리스트 초기화"""
        if not url_list:
            raise ValueError("URL 리스트가 비어있습니다.")
        self.urls = list(url_list)
        self.current_batch_results = ([], [])
        logger.log("info", f"{len(url_list)}개의 URL이 초기화되었습니다.")

    def _process_single_url(self, url: str) -> tuple[bool, Optional[dict]]:
        """단일 URL 처리"""
        try:
            success, webtoon_data = self.scraper.fetch_webtoon(url)
            if success and webtoon_data:
                return True, webtoon_data.to_dict()
            return False, None
        except Exception as e:
            logger.log("error", f"URL 처리 중 오류 발생: {url}, 오류: {e}")
            return False, None

    def _process_batch(self, url_batch: List[str]) -> tuple[List[dict], List[dict]]:
        """배치 단위 URL 처리"""
        success_batch = []
        failure_batch = []

        for url in url_batch:
            success, webtoon_data = self._process_single_url(url)
            if success and webtoon_data:
                success_batch.append(webtoon_data)
            else:
                failure_batch.append({"url": url, "error": "데이터 수집 실패"})

        return success_batch, failure_batch

    def run(self) -> None:
        """크롤링 실행"""
        if not self.urls:
            raise ValueError("URL 리스트가 초기화되지 않았습니다.")
        
        if self.is_running:
            raise RuntimeError("크롤러가 이미 실행 중입니다.")

        self.is_running = True
        try:
            for success_batch, failure_batch in self.batch_processor.process_in_batches(self.urls, self._process_batch):
                # 각 배치의 결과를 누적
                self.current_batch_results = (
                    self.current_batch_results[0] + success_batch,
                    self.current_batch_results[1] + failure_batch
                )
                logger.log("info", f"현재까지 누적: 성공 {len(self.current_batch_results[0])}, 실패 {len(self.current_batch_results[1])}")
        finally:
            self.is_running = False

    def get_results(self) -> Tuple[List[dict], List[dict]]:
        """현재까지의 크롤링 결과 반환"""
        return self.current_batch_results

    def shutdown(self) -> None:
        """리소스 정리"""
        try:
            self.driver.quit()
        except Exception as e:
            logger.log("error", f"WebDriver 종료 중 오류 발생: {e}")
        else:
            logger.log("info", "WebDriver 종료 완료.")