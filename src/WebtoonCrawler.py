import logging
from src.WebDriver import ChromeWebDriverFactory
from src.Repository import WebtoonRepositoryFactory
from src.Scraper import WebtoonScraperFactory
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# WebtoonCrawler 클래스: 개선된 구조 및 에러 처리
class WebtoonCrawler:
    def __init__(self, scraper_type: str, driver_path: str, repository_type: str):
        logger.info("Initializing WebtoonCrawler")
        self.driver_factory = ChromeWebDriverFactory(driver_path)
        self.driver = self.driver_factory.create_driver()
        self.repository = WebtoonRepositoryFactory.create_repository(repository_type)
        self.scraper = WebtoonScraperFactory.create_scraper(scraper_type, self.driver)

    def run(self):
        try:
            logger.info("Starting webtoon crawling process")
            self._process_webtoons()
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            self.save_and_cleanup()

    def _process_webtoons(self):
        urls = self.scraper.get_urls()
        for url in urls:
            try:
                self.scraper.open_page(url)
                webtoon_elements = self.scraper.get_webtoon_elements()

                if not webtoon_elements:
                    logger.warning(f"No webtoon elements found for URL: {url}")
                    continue

                self._process_elements(webtoon_elements)
            except WebDriverException as e:
                logger.error(f"WebDriverException encountered while processing URL {url}: {e}")
                continue

    def _process_elements(self, webtoon_elements):
        webtoon_list_len = len(webtoon_elements)
        for i in range(webtoon_list_len):
            try:
                logger.info(f"Processing: {i + 1} / {webtoon_list_len}")

                webtoon_elements = self.scraper.get_webtoon_elements()
                webtoon_data = self.scraper.scrape_webtoon_info(webtoon_elements[i])

                if webtoon_data:
                    self.repository.save(webtoon_data)
            except StaleElementReferenceException:
                logger.error(f"StaleElementReferenceException encountered on element {i + 1}. Retrying...")
                continue
            except WebDriverException as e:
                logger.error(f"WebDriverException encountered: {e}. Retrying...")
                self.scraper.driver.refresh()
                continue

    def save_and_cleanup(self):
        try:
            scraper_type = self.scraper.__class__.__name__.lower()
            self.repository.save_to_file(scraper_type + "_webtoon_list")
            logger.info(f"Data saved successfully for scraper type: {scraper_type}")
        finally:
            self.driver.quit()
            logger.info("WebDriver closed successfully")