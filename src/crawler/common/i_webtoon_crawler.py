from typing import List, Tuple

class IWebtoonCrawler:
    def initialize(self, url_list: List[str]) -> None:
        pass

    def run(self) -> None:
        pass

    def get_results(self) -> Tuple[List[dict], List[dict]]:
        pass

    def shutdown(self) -> None:
        pass