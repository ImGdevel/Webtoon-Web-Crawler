from crawler.common.i_webtoon_crawler import IWebtoonCrawler
from typing import List

class StatusCheckCrawler(IWebtoonCrawler):
    def __init__(self):
        # 셋업: driver, scraper 등
        pass

    def initialize(self, url_list: List[str]) -> None:
        pass

    def run(self) -> None:
        # 각 웹툰이 연재 중인지, 완결인지 등 상태만 확인
        pass

    def save(self) -> None:
        pass

    def shutdown(self) -> None:
        pass
