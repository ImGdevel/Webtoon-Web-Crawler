from modules.webtoon_list_manager import WebtoonListManager
from modules.webtoon_repository import WebtoonRepository
from scrapers import WebtoonListScraper
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory

def save_crawler_results(success_data: list, failed_data: list, repository: WebtoonRepository) -> None:
    """크롤러 결과를 저장하는 함수"""
    if success_data:
        repository.append_success(success_data)
    if failed_data:
        repository.append_failure(failed_data)

if __name__ == "__main__":
    # 저장소 초기화
    repository = WebtoonRepository("webtoon_data.json", "failed_webtoon_list.json")
    
    # 크롤러 초기화
    crawler = WebtoonCrawlerFactory.create_crawler(task_name="test")
    
    try:
        # URL 목록 초기화
        list_manager = WebtoonListManager("webtoon_urls.txt")
        if not list_manager.load_urls_from_txt():
            list_scraper = WebtoonListScraper(crawler.driver)
            list_manager.collect_webtoon_urls(list_scraper)

        # 크롤링 실행
        crawler.initialize(list_manager.urls)
        crawler.run()
        
        # 결과 저장
        success_data, failed_data = crawler.get_results()
        save_crawler_results(success_data, failed_data, repository)
    
    except KeyboardInterrupt:
        print("\n[사용자 중단] Ctrl+C 감지됨. 안전하게 종료 중...")
        # 강제 종료 시 현재까지의 배치 결과 저장
        success_data, failed_data = crawler.get_results()
        save_crawler_results(success_data, failed_data, repository)
    finally:
        crawler.shutdown()
