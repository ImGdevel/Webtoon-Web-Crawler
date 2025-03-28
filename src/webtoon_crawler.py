from logger import Logger
from typing import List, Set
import os
from modules.chrome_webdriver_manager import ChromeWebDriverManager
from modules.webtoon_repository import WebtoonRepository
from modules.webtoon_list_manager import WebtoonListManager
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory
from scrapers.webtoon_list_scraper import WebtoonListScraper

logger = Logger()

class WebtoonCrawler:
    """웹툰 크롤러 클래스"""

    NAVER_WEBTOON_URLS = [
        "https://comic.naver.com/webtoon?tab=finish",
        "https://comic.naver.com/webtoon?tab=mon",
        "https://comic.naver.com/webtoon?tab=tue",
        "https://comic.naver.com/webtoon?tab=wed",
        "https://comic.naver.com/webtoon?tab=thu",
        "https://comic.naver.com/webtoon?tab=fri",
        "https://comic.naver.com/webtoon?tab=sat",
        "https://comic.naver.com/webtoon?tab=sun",
    ]
    BATCH_SIZE = 10

    def __init__(self):
        self.driver_manager = ChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraperFactory.create_scraper(self.driver, "naver")
        self.list_scraper = WebtoonListScraper(self.driver)
        self.repository = WebtoonRepository("webtoon_data.json", "failed_webtoon_list.json")
        self.list_manager = WebtoonListManager("webtoon_urls.txt")

    def initialize_urls(self) -> None:
        """URL 초기화 메서드: 파일에서 로드하거나 새로 수집"""
        if not self.list_manager.load_urls_from_txt():
            logger.log("info", "새로운 URL 수집을 시작합니다.")
            self.list_manager.collect_webtoon_urls(self.list_scraper)

    def process_batch(self, url_batch: List[str]) -> tuple[List[dict], List[dict]]:
        """배치 단위로 웹툰 정보를 처리"""
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
        """크롤링 실행 메서드"""
        self.initialize_urls()
        logger.log("info", f"총 {len(self.list_manager.urls)}개의 웹툰 URL에 대해 크롤링을 시작합니다.")

        url_list = list(self.list_manager.urls)
        total_batches = (len(url_list) + self.BATCH_SIZE - 1) // self.BATCH_SIZE

        for batch_num in range(total_batches):
            start_idx = batch_num * self.BATCH_SIZE
            end_idx = min((batch_num + 1) * self.BATCH_SIZE, len(url_list))
            current_batch = url_list[start_idx:end_idx]

            logger.log("info", f"배치 {batch_num + 1}/{total_batches} 처리 중... ({start_idx + 1}~{end_idx})")
            
            success_batch, failure_batch = self.process_batch(current_batch)
            
            if success_batch:
                self.repository.append_success(success_batch)
            if failure_batch:
                self.repository.append_failure(failure_batch)

            logger.log("info", f"배치 {batch_num + 1} 완료: 성공 {len(success_batch)}, 실패 {len(failure_batch)}")

        self.driver.quit()
        logger.log("info", "모든 배치 처리 완료")

if __name__ == "__main__":
    crawler = WebtoonCrawler()
    crawler.run()
