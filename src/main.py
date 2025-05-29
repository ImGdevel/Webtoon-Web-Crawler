from crawler.init_webtoon_crawler import InitWebtoonCrawler
from modules.webtoon_list_manager import WebtoonListManager
from scrapers.webtoon_list_scraper import WebtoonListScraper

if __name__ == "__main__":
    crawler = InitWebtoonCrawler()
    
    try:
        list_manager = WebtoonListManager("webtoon_urls.txt")
        if not list_manager.load_urls_from_txt():
            list_scraper = WebtoonListScraper(crawler.driver)
            list_manager.collect_webtoon_urls(list_scraper)

        crawler.initialize(list_manager.urls)

        crawler.run()
    
    except KeyboardInterrupt:
        print("\n[사용자 중단] Ctrl+C 감지됨. 안전하게 종료 중...")
