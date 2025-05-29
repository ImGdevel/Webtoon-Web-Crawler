from typing import Optional
from crawler.common.i_webtoon_crawler import IWebtoonCrawler
from modules.web_driver.web_driver_factory import WebDriverFactory

class WebtoonCrawlerFactory:
    """웹툰 크롤러 팩토리 클래스"""
    
    def __init__(self, web_driver_factory: Optional[WebDriverFactory] = None):
        """
        웹툰 크롤러 팩토리 초기화
        
        Args:
            web_driver_factory (WebDriverFactory, optional): 웹 드라이버 팩토리 인스턴스
        """
        self.web_driver_factory = web_driver_factory or WebDriverFactory()

    def create_crawler(self, task_name: str, environment: Optional[str] = None, show_browser: bool = False) -> IWebtoonCrawler:
        """
        크롤러 생성
        
        Args:
            task_name (str): 크롤러 작업 이름
            environment (str, optional): 실행 환경 ("local", "lambda", "docker_lambda")
            show_browser (bool, optional): 브라우저 표시 여부. True면 브라우저가 보이고, False면 headless 모드로 실행
            
        Returns:
            IWebtoonCrawler: 생성된 크롤러 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 작업 이름이 지정된 경우
        """
        task_name = task_name.lower()

        if task_name == "collect_episodes":
            from crawler import EpisodeCollectorCrawler
            return EpisodeCollectorCrawler(
                driver_manager=self.web_driver_factory.create_driver(environment=environment, headless=not show_browser)
            )
        elif task_name == "check_status":
            from crawler import StatusCheckCrawler
            return StatusCheckCrawler(
                driver_manager=self.web_driver_factory.create_driver(environment=environment, headless=not show_browser)
            )
        elif task_name == "test" or task_name == "update":
            from crawler.tasks.init_webtoon_crawler import InitWebtoonCrawler
            return InitWebtoonCrawler(
                driver_manager=self.web_driver_factory.create_driver(environment=environment, headless=not show_browser)
            )
        else:
            # 향후 다른 크롤러가 생기면 여기에 추가
            raise ValueError(f"알 수 없는 작업 이름: {task_name}")
