from src.WebDriver.WebDriverFactory import ChromeWebDriverFactory
from src.Repository.WebtoonRepository import JsonWebtoonRepository
from src.Scraper.WebtoonScraper import NaverWebtoonScraper, KaKaoWebtoonScraper
from src.Crawler.WebtoonCrawler import WebtoonCrawler

def main():
    driver_factory = ChromeWebDriverFactory('C:/chromedriver-win64/chromedriver.exe')
    driver = driver_factory.create_driver()
    repository = JsonWebtoonRepository()

    scraper_type = 'naver'

    if scraper_type == 'naver':
        scraper = NaverWebtoonScraper(driver)
    elif scraper_type == 'kakao':
        scraper = KaKaoWebtoonScraper(driver)

    crawler = WebtoonCrawler(scraper, repository)

    try:
        crawler.run()
    finally:
        repository.save_to_json(scraper_type+"_webtoon_list")
        input("프로그램을 종료하려면 엔터를 누르세요...")
        driver.quit()

if __name__ == "__main__":
    main()
