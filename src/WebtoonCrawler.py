from src.WebDriver.WebDriverFactory import ChromeWebDriverFactory
from src.Repository.WebtoonRepository import WebtoonRepository
from src.Scraper.WebtoonScraper import WebtoonScraper
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from src.WebDriver.WebDriverFactory import ChromeWebDriverFactory
from src.Repository.WebtoonRepository import JsonWebtoonRepository
from src.Scraper.WebtoonScraperFactory import WebtoonScraperFactory
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

class WebtoonCrawler:
    def __init__(self, scraper_type: str, driver_path: str, repository_path: str):
        self.driver_factory = ChromeWebDriverFactory(driver_path)
        self.driver = self.driver_factory.create_driver()
        self.repository = JsonWebtoonRepository()
        self.scraper = WebtoonScraperFactory.create_scraper(scraper_type, self.driver)

    def run(self):
        for url in self.scraper.get_urls():
            self.scraper.open_page(url)
            webtoon_elements = self.scraper.get_webtoon_elements()

            if not webtoon_elements:
                print("No webtoon elements found. Exiting...")
                continue

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
        self.repository.save_to_json(scraper_type + "_webtoon_list")
        self.driver.quit()