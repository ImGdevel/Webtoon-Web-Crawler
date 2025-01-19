from src.WebDriver import ChromeWebDriverFactory
from src.Repository import WebtoonRepositoryFactory
from src.Scraper import WebtoonScraperFactory
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

# Crawler 클래스
class WebtoonCrawler:
    def __init__(self, scraper_type: str, driver_path: str, repository_type: str):
        self.driver_factory = ChromeWebDriverFactory(driver_path)
        self.driver = self.driver_factory.create_driver()
        self.repository = WebtoonRepositoryFactory.create_repository(repository_type)
        self.scraper = WebtoonScraperFactory.create_scraper(scraper_type, self.driver)

    def run(self):
        try:
            self._process_webtoons()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.save_and_cleanup(self.scraper.__class__.__name__.lower())

    def _process_webtoons(self):
        for url in self.scraper.get_urls():
            self.scraper.open_page(url)
            webtoon_elements = self.scraper.get_webtoon_elements()

            if not webtoon_elements:
                print("No webtoon elements found. Exiting...")
                continue

            self._process_elements(webtoon_elements)

    def _process_elements(self, webtoon_elements):
        webtoon_list_len = len(webtoon_elements)
        for i in range(webtoon_list_len):
            try:
                print(f"Processing: {i + 1} / {webtoon_list_len}")

                webtoon_elements = self.scraper.get_webtoon_elements()
                webtoon_data = self.scraper.scrape_webtoon_info(webtoon_elements[i])

                if webtoon_data:
                    self.repository.save(webtoon_data)
            except StaleElementReferenceException:
                print(f"StaleElementReferenceException encountered on element {i + 1}. Retrying...")
                continue
            except WebDriverException as e:
                print(f"WebDriverException encountered: {e}. Retrying...")
                self.scraper.driver.refresh()
                continue

    def save_and_cleanup(self, scraper_type: str):
        self.repository.save_to_file(scraper_type + "_webtoon_list")
        self.driver.quit()

