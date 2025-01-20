import gc
import logging
from src.WebDriver import ChromeWebDriverFactory
from src.Repository import WebtoonRepositoryFactory
from src.Scraper import WebtoonScraperFactory
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class WebtoonCrawler:
    def __init__(self, scraper_type: str, driver_path: str, repository_type: str):
        logger.info("Initializing WebtoonCrawler")
        self.driver_factory = ChromeWebDriverFactory(driver_path)
        self.repository = WebtoonRepositoryFactory.create_repository(repository_type)
        self.scraper_type = scraper_type
        self.driver = None
        self.scraper = None

    def _reset_driver(self):
        if self.driver:
            self.driver.quit()
        self.driver = self.driver_factory.create_driver()
        self.scraper = WebtoonScraperFactory.create_scraper(self.scraper_type, self.driver)

    def run(self):
        try:
            logger.info("Starting webtoon crawling process")
            self._reset_driver()
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

                self._process_elements(webtoon_elements, url)

            except WebDriverException as e:
                logger.error(f"WebDriverException encountered while processing URL {url}: {e}")
                continue
            finally:
                gc.collect()


    def _process_elements(self, webtoon_elements, url):
        batch_size = 40
        total_elements = len(webtoon_elements)
        processed_count = 0

        for batch_start in range(0, total_elements, batch_size):
            batch_end = min(batch_start + batch_size, total_elements)
            batch = webtoon_elements[batch_start:batch_end]
            logger.info(f"Processing batch {batch_start + 1}-{batch_end} of {total_elements}")

            for i, element in enumerate(batch):
                retry_count = 0
                max_retries = 3

                while retry_count < max_retries:
                    try:
                        logger.info(f"Processing webtoon element {batch_start + i + 1}/{total_elements} (Attempt {retry_count + 1})")

                        # 리스트 갱신 후 유효성 검증
                        webtoon_elements = self.scraper.get_webtoon_elements()
                        if not webtoon_elements or batch_start + i >= len(webtoon_elements):
                            logger.warning("Webtoon elements list is invalid or index out of range. Skipping element.")
                            break

                        # 데이터 스크래핑
                        webtoon_data = self.scraper.scrape_webtoon_info(webtoon_elements[batch_start + i])
                        if webtoon_data:
                            self.repository.save(webtoon_data)
                        break
                    except StaleElementReferenceException:
                        retry_count += 1
                        logger.warning(f"Stale element encountered on element {batch_start + i + 1}. Retrying... ({retry_count}/{max_retries})")
                        if retry_count >= max_retries:
                            logger.error(f"Max retries reached for element {batch_start + i + 1}. Skipping...")
                            self.scraper.open_page(url)
                            break
                    except IndexError:
                        logger.error(f"IndexError: list index out of range for element {batch_start + i + 1}. Skipping...")
                        break
                    except WebDriverException as e:
                        logger.error(f"WebDriverException encountered: {e}. Returning to URL...")
                        self.scraper.open_page(url)
                        break

            processed_count += len(batch)
            if processed_count % (batch_size * 2) == 0:
                self._restart_webdriver()
                self.scraper.open_page(url)
                webtoon_elements = self.scraper.get_webtoon_elements()

            del batch
            gc.collect()



    def _restart_webdriver(self):
        logger.info("Restarting WebDriver to free up resources")
        try:
            # 기존 드라이버 종료
            self.driver.quit()
            logger.info("WebDriver quit successfully")

            # 새 드라이버 생성
            self.driver = self.driver_factory.create_driver()
            self.scraper.driver = self.driver 
            logger.info("WebDriver restarted successfully")
        except Exception as e:
            logger.error(f"Failed to restart WebDriver: {e}", exc_info=True)
            raise


    def save_and_cleanup(self):
        try:
            if self.scraper:
                scraper_type = self.scraper.__class__.__name__.lower()
                self.repository.save_to_file(scraper_type + "_webtoon_list")
                logger.info(f"Data saved successfully for scraper type: {scraper_type}")
        finally:
            if self.driver:
                self.driver.quit()
            logger.info("WebDriver closed successfully")
