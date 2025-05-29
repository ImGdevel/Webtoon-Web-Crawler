from modules.webtoon_list_manager import WebtoonListManager
from scrapers import WebtoonListScraper
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory

if __name__ == "__main__":

    crawler = WebtoonCrawlerFactory.create_crawler(task_name="test")
    
    try:
        list_manager = WebtoonListManager("webtoon_urls.txt")
        if not list_manager.load_urls_from_txt():
            list_scraper = WebtoonListScraper(crawler.driver)
            list_manager.collect_webtoon_urls(list_scraper)

        crawler.initialize(list_manager.urls)

        crawler.run()
    
    except KeyboardInterrupt:
        print("\n[사용자 중단] Ctrl+C 감지됨. 안전하게 종료 중...")
