from crawler.common.i_webtoon_crawler import IWebtoonCrawler
from typing import List

class EpisodeCollectorCrawler(IWebtoonCrawler):
    def __init__(self):
        # 셋업: driver, scraper, repository 등
        pass

    def initialize(self, url_list: List[str]) -> None:
        pass

    def run(self) -> None:
        # 각 웹툰 URL에서 에피소드 목록 긁어오기
        pass

    def get_results(self) -> None:
        pass

    def shutdown(self) -> None:
        pass
