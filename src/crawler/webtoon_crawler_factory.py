from crawler.i_webtoon_crawler import IWebtoonCrawler

class WebtoonCrawlerFactory:
    @staticmethod
    def create_crawler(task_name: str) -> IWebtoonCrawler:
        task_name = task_name.lower()

        if task_name == "collect_episodes":
            from crawler.EpisodeCollectorCrawler import EpisodeCollectorCrawler
            return EpisodeCollectorCrawler()
        elif task_name == "check_status":
            from crawler.StatusCheckCrawler import StatusCheckCrawler
            return StatusCheckCrawler()
        elif task_name == "test":
            from crawler.init_webtoon_crawler import InitWebtoonCrawler
            return InitWebtoonCrawler()
        else:
            # 향후 다른 크롤러가 생기면 여기에 추가
            raise ValueError(f"알 수 없는 작업 이름: {task_name}")
