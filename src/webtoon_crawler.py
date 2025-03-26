from logger import Logger 
from typing import List
from modules.chrome_webdriver_manager import ChromeWebDriverManager
from modules.webtoon_repository import WebtoonRepository
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory
from scrapers.webtoon_list_scraper import WebtoonListScraper

logger = Logger()

class WebtoonCrawler:
    """웹툰 크롤러 클래스"""

    NAVER_WEBTOON_URLS = [
        "https://comic.naver.com/webtoon?tab=mon",
        "https://comic.naver.com/webtoon?tab=tue",
        "https://comic.naver.com/webtoon?tab=wed",
        "https://comic.naver.com/webtoon?tab=thu",
        "https://comic.naver.com/webtoon?tab=fri",
        "https://comic.naver.com/webtoon?tab=sat",
        "https://comic.naver.com/webtoon?tab=sun",
    ]

    def __init__(self):
        self.urls: List[str] = [] 
        self.driver_manager = ChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraperFactory.create_scraper(self.driver, "naver")
        self.list_scraper = WebtoonListScraper(self.driver)
        self.success_list: List[dict] = []
        self.failure_list: List[dict] = []
        self.repository = WebtoonRepository("webtoon_data.json", "failed_webtoon_list.json")

    def collect_webtoon_urls(self) -> None:
        """네이버 웹툰 요일별 페이지에서 모든 웹툰 URL을 수집"""
        for page_url in self.NAVER_WEBTOON_URLS:
            logger.log("info", f"웹툰 리스트 크롤링 시작: {page_url}")
            webtoon_urls = self.list_scraper.get_webtoon_urls(page_url)
            self.urls.extend(webtoon_urls)

    def run(self) -> None:
        """크롤링 실행 메서드"""
        self.collect_webtoon_urls()  # 웹툰 목록 URL 수집

        for url in self.urls:
            success, webtoon_data = self.scraper.fetch_webtoon(url)
            if success and webtoon_data:
                self.success_list.append(webtoon_data.to_dict())
            else:
                self.failure_list.append({"url": url})

        self.save_results()
        self.driver.quit()

    def save_results(self):
        """크롤링 결과를 JSON 파일로 저장"""
        self.repository.save_success(self.success_list)
        self.repository.save_failure(self.failure_list)

if __name__ == "__main__":
    crawler = WebtoonCrawler()
    crawler.run()
