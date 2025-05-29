import atexit
from utils.logger import logger
from typing import List
from modules.web_driver.local_chrome_webdriver_manager import LocalChromeWebDriverManager
from modules.webtoon_repository import WebtoonRepository
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory
from crawler import IWebtoonCrawler

class InitWebtoonCrawler(IWebtoonCrawler):
    """웹툰 크롤러 클래스"""

    BATCH_SIZE = 10

    def __init__(self):
        self.driver_manager = LocalChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraperFactory.create_basic_info_scraper(self.driver, platform="naver")
        self.repository = WebtoonRepository("webtoon_data.json", "failed_webtoon_list.json")

        self.urls: List[str] = []
        self.success_data: List[dict] = []
        self.failed_data: List[dict] = []

        # 종료 시 save 자동 호출
        atexit.register(self._safe_exit)

    def _safe_exit(self):
        """종료 시 안전하게 저장 및 셧다운"""
        try:
            self.save()
        finally:
            self.shutdown()

    def initialize(self, url_list: List[str]) -> None:
        self.urls = list(url_list)
        logger.log("info", f"{len(url_list)}개의 URL이 초기화되었습니다.")

    def process_batch(self, url_batch: List[str]) -> tuple[List[dict], List[dict]]:
        success_batch = []
        failure_batch = []

        for url in url_batch:
            success, webtoon_data = self.scraper.fetch_webtoon(url)
            if success and webtoon_data:
                success_batch.append(webtoon_data.to_dict())
            else:
                failure_batch.append({"url": url})

        return success_batch, failure_batch

    def run(self) -> None:

        if not self.urls:
            raise ValueError("URL 리스트가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        total_batches = (len(self.urls) + self.BATCH_SIZE - 1) // self.BATCH_SIZE

        for batch_num in range(total_batches):
            start_idx = batch_num * self.BATCH_SIZE
            end_idx = min((batch_num + 1) * self.BATCH_SIZE, len(self.urls))
            current_batch = self.urls[start_idx:end_idx]

            logger.log("info", f"배치 {batch_num + 1}/{total_batches} 처리 중... ({start_idx + 1}~{end_idx})")

            success_batch, failure_batch = self.process_batch(current_batch)

            # 메모리에만 저장 (디스크 저장은 shutdown 시점에)
            self.success_data.extend(success_batch)
            self.failed_data.extend(failure_batch)

            logger.log("info", f"배치 {batch_num + 1} 완료: 성공 {len(success_batch)}, 실패 {len(failure_batch)}")

    def save(self) -> None:
        if self.success_data:
            self.repository.append_success(self.success_data)
        if self.failed_data:
            self.repository.append_failure(self.failed_data)

        logger.log("info", f"[자동 저장] 저장 완료: 성공 {len(self.success_data)}, 실패 {len(self.failed_data)}")

    def shutdown(self) -> None:
        try:
            self.driver.quit()
        except Exception:
            logger.log("error", "WebDriver 종료 중 오류 발생")
        else:
            logger.log("info", "WebDriver 종료 완료.")

