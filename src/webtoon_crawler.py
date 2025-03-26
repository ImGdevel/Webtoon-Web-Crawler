from logger import Logger 
from typing import List
from modules.chrome_webdriver_manager import ChromeWebDriverManager
from modules.webtoon_repository import WebtoonRepository
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory

logger = Logger()

class WebtoonCrawler:
    """웹툰 크롤러 클래스"""

    def __init__(self):
        self.urls: List[str] = [] 
        self.driver_manager = ChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraperFactory.create_scraper(self.driver, "naver")
        self.success_list: List[dict] = []
        self.failure_list: List[dict] = []
        self.repository = WebtoonRepository("webtoon_data.json", "failed_webtoon_list.json")

    def set_urls(self, urls: List[str]) -> None:
        """URL 리스트를 추가하는 메서드"""
        self.urls.extend(urls)

    def run(self) -> None:
        """크롤링 실행 메서드"""
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
    urls_to_add = [
        "https://comic.naver.com/webtoon/list?titleId=747271",
        "https://comic.naver.com/webtoon/list?titleId=769209",
        "https://comic.naver.com/webtoon/list?titleId=776601",
        "https://comic.naver.com/webtoon/list?titleId=822657",
    ]
    crawler.set_urls(urls_to_add)
    crawler.run()
