from src.WebtoonCrawler import WebtoonCrawler

def main():
    scraper_type = 'naver'
    driver_path = 'C:/chromedriver-win64/chromedriver.exe'
    repository_path = 'webtoon_data.json'

    crawler = WebtoonCrawler(scraper_type, driver_path, repository_path)

    try:
        crawler.run()
    finally:
        crawler.save_and_cleanup(scraper_type)
        input("프로그램을 종료하려면 엔터를 누르세요...")

if __name__ == "__main__":
    main()
