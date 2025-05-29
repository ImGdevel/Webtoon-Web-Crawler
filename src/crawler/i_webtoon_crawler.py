from typing import List, Tuple

class IWebtoonCrawler:
    def initialize_urls(self) -> None:
        pass

    def process_batch(self, url_batch: List[str]) -> Tuple[List[dict], List[dict]]:
        pass

    def run(self) -> None:
        pass