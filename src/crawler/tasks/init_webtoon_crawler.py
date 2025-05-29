import atexit
from typing import List, Optional
from utils.logger import logger
from modules.web_driver import IWebDriverManager, WebDriverFactory
from modules.webtoon_repository import WebtoonRepository
from scrapers.webtoon_scraper_factory import WebtoonScraperFactory
from crawler import IWebtoonCrawler
from selenium.webdriver.remote.webdriver import WebDriver

class BatchProcessor:
    """배치 처리를 담당하는 클래스"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size

    def process_in_batches(self, items: List[str], process_func) -> tuple[List[dict], List[dict]]:
        """아이템들을 배치 단위로 처리"""
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        all_success = []
        all_failure = []

        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min((batch_num + 1) * self.batch_size, len(items))
            current_batch = items[start_idx:end_idx]

            logger.log("info", f"배치 {batch_num + 1}/{total_batches} 처리 중... ({start_idx + 1}~{end_idx})")
            
            success_batch, failure_batch = process_func(current_batch)
            all_success.extend(success_batch)
            all_failure.extend(failure_batch)

            logger.log("info", f"배치 {batch_num + 1} 완료: 성공 {len(success_batch)}, 실패 {len(failure_batch)}")

        return all_success, all_failure

class DataStorageService:
    """데이터 저장을 담당하는 서비스 클래스"""
    
    def __init__(self, repository: WebtoonRepository):
        self.repository = repository
        self.success_data: List[dict] = []
        self.failed_data: List[dict] = []

    def add_success(self, data: List[dict]) -> None:
        """성공 데이터 추가"""
        self.success_data.extend(data)

    def add_failure(self, data: List[dict]) -> None:
        """실패 데이터 추가"""
        self.failed_data.extend(data)

    def save(self) -> None:
        """데이터 저장"""
        if self.success_data:
            self.repository.append_success(self.success_data)
        if self.failed_data:
            self.repository.append_failure(self.failed_data)

        logger.log("info", f"[자동 저장] 저장 완료: 성공 {len(self.success_data)}, 실패 {len(self.failed_data)}")

class InitWebtoonCrawler(IWebtoonCrawler):
    """웹툰 초기화 크롤러 클래스"""

    def __init__(
        self,
        driver_manager: Optional[IWebDriverManager] = None,
        repository: Optional[WebtoonRepository] = None,
        batch_size: int = 10
    ):
        
        self.driver_manager = driver_manager or WebDriverFactory.create_driver(headless=True)
        self.driver: WebDriver = self.driver_manager.get_driver()
        self.scraper = WebtoonScraperFactory.create_basic_info_scraper(self.driver, platform="naver")
        self.repository = repository or WebtoonRepository("webtoon_data.json", "failed_webtoon_list.json")
        
        # 서비스 초기화
        self.batch_processor = BatchProcessor(batch_size)
        self.storage_service = DataStorageService(self.repository)
        
        self.urls: List[str] = []
        
        # 종료 시 save 자동 호출
        atexit.register(self._safe_exit)

    def _safe_exit(self):
        """종료 시 안전하게 저장 및 셧다운"""
        try:
            self.storage_service.save()
        finally:
            self.shutdown()

    def initialize(self, url_list: List[str]) -> None:
        """URL 리스트 초기화"""
        if not url_list:
            raise ValueError("URL 리스트가 비어있습니다.")
        self.urls = list(url_list)
        logger.log("info", f"{len(url_list)}개의 URL이 초기화되었습니다.")

    def _process_single_url(self, url: str) -> tuple[bool, Optional[dict]]:
        """단일 URL 처리"""
        try:
            success, webtoon_data = self.scraper.fetch_webtoon(url)
            if success and webtoon_data:
                return True, webtoon_data.to_dict()
            return False, None
        except Exception as e:
            logger.log("error", f"URL 처리 중 오류 발생: {url}, 오류: {e}")
            return False, None

    def _process_batch(self, url_batch: List[str]) -> tuple[List[dict], List[dict]]:
        """배치 단위 URL 처리"""
        success_batch = []
        failure_batch = []

        for url in url_batch:
            success, webtoon_data = self._process_single_url(url)
            if success and webtoon_data:
                success_batch.append(webtoon_data)
            else:
                failure_batch.append({"url": url, "error": "데이터 수집 실패"})

        return success_batch, failure_batch

    def run(self) -> None:
        """크롤링 실행"""
        if not self.urls:
            raise ValueError("URL 리스트가 초기화되지 않았습니다. initialize()를 먼저 호출하세요.")

        success_data, failed_data = self.batch_processor.process_in_batches(
            self.urls,
            self._process_batch
        )

        self.storage_service.add_success(success_data)
        self.storage_service.add_failure(failed_data)

    def shutdown(self) -> None:
        """리소스 정리"""
        try:
            self.driver.quit()
        except Exception as e:
            logger.log("error", f"WebDriver 종료 중 오류 발생: {e}")
        else:
            logger.log("info", "WebDriver 종료 완료.")

