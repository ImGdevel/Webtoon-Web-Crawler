from src.WebDriver.WebDriverFactory import ChromeWebDriverFactory
from src.Repository.WebtoonRepository import JsonWebtoonRepository
from src.Scraper.WebtoonScraperFactory import WebtoonScraperFactory
from src.Crawler.WebtoonCrawler import WebtoonCrawler

def main():
    driver_factory = ChromeWebDriverFactory('C:/chromedriver-win64/chromedriver.exe')
    driver = driver_factory.create_driver()
    repository = JsonWebtoonRepository()

    scraper_type = 'naver'  # 또는 'kakao'

    try:
        # Scraper Factory를 사용해 스크래퍼 생성
        scraper = WebtoonScraperFactory.create_scraper(scraper_type, driver)
        crawler = WebtoonCrawler(scraper, repository)

        crawler.run()
    finally:
        repository.save_to_json(scraper_type + "_webtoon_list")
        input("프로그램을 종료하려면 엔터를 누르세요...")
        driver.quit()

if __name__ == "__main__":
    main()
