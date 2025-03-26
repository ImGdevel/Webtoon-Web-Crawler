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
        self.scraper_type = scraper_type
        self.driver_factory = ChromeWebDriverFactory(driver_path)
        self.driver = self.driver_factory.create_driver()
        self.repository = WebtoonRepositoryFactory.create_repository(repository_type)
        self.scraper = WebtoonScraperFactory.create_scraper(self.scraper_type, self.driver)

    def run(self):
        try:
            logger.info("Starting webtoon crawling process")
            self._process_webtoons()
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            if self.driver:
                self.driver.quit()

    def _process_webtoons(self):
        urls = self.scraper.get_urls()

        for url in urls:
            try:
                self.scraper.open_page(url)
                webtoon_elements = self.scraper.get_webtoon_elements()

                if not webtoon_elements:
                    logger.warning(f"No webtoon elements found for URL: {url}")
                    continue

                self._process_elements_in_batches(webtoon_elements, url)

            except WebDriverException as e:
                logger.error(f"WebDriverException encountered while processing URL {url}: {e}")
                continue
            finally:
                self.save_and_cleanup()
                self._restart_webdriver()
                gc.collect()

    def _process_elements_in_batches(self, webtoon_elements, url, batch_size=40):
        total_elements = len(webtoon_elements)
        processed_count = 0

        for batch_start in range(0, total_elements, batch_size):
            batch_end = min(batch_start + batch_size, total_elements)
            batch = webtoon_elements[batch_start:batch_end]
            logger.info(f"Processing batch {batch_start + 1}-{batch_end} of {total_elements}")

            self._process_batch(batch, batch_start, total_elements, url)

            processed_count += len(batch)
            if processed_count % (batch_size * 2) == 0:
                self._restart_webdriver()
                self.scraper.open_page(url)
                webtoon_elements = self.scraper.get_webtoon_elements()

            del batch
            gc.collect()

    def _process_batch(self, batch, batch_start, total_elements, url):
        for i, element in enumerate(batch):
            self._process_single_element(batch_start + i, element, total_elements, url)

    def _process_single_element(self, element_index, element, total_elements, url):
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                logger.info(f"Processing webtoon element {element_index + 1}/{total_elements} (Attempt {retry_count + 1})")

                webtoon_elements = self.scraper.get_webtoon_elements()
                if not webtoon_elements or element_index >= len(webtoon_elements):
                    logger.warning("Webtoon elements list is invalid or index out of range. Skipping element.")
                    break

                webtoon_data = self.scraper.scrape_webtoon_info(webtoon_elements[element_index])
                if webtoon_data:
                    self.repository.save(webtoon_data)
                break
            except StaleElementReferenceException:
                retry_count += 1
                logger.warning(f"Stale element encountered on element {element_index + 1}. Retrying... ({retry_count}/{max_retries})")
                if retry_count >= max_retries:
                    logger.error(f"Max retries reached for element {element_index + 1}. Skipping...")
                    self.scraper.open_page(url)
                    break
            except IndexError:
                logger.error(f"IndexError: list index out of range for element {element_index + 1}. Skipping...")
                break
            except WebDriverException as e:
                logger.error(f"WebDriverException encountered: {e}. Returning to URL...")
                self.scraper.open_page(url)
                break

    def _restart_webdriver(self):
        logger.info("Restarting WebDriver to free up resources")
        try:
            self.driver.quit()
            logger.info("WebDriver quit successfully")

            self.driver = self.driver_factory.create_driver()
            self.scraper.driver = self.driver
            logger.info("WebDriver restarted successfully")
        except Exception as e:
            logger.error(f"Failed to restart WebDriver: {e}", exc_info=True)
            raise

    def save_and_cleanup(self):
            try:
                scraper_type = self.scraper.__class__.__name__.lower()
                self.repository.save_to_file(scraper_type + "_webtoon_list")
                logger.info(f"Data saved successfully for scraper type: {scraper_type}")
            finally:
                self.driver.quit()
                logger.info("WebDriver closed successfully")