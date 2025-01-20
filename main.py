from src.WebtoonCrawler import WebtoonCrawler

def main():
    scraper_type = 'naver'
    driver_path = 'C:/chromedriver-win64/chromedriver.exe'
    repository_type = 'json'

    crawler = WebtoonCrawler(scraper_type, driver_path, repository_type)
    crawler.run()


if __name__ == "__main__":
    main()
