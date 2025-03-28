import os
from typing import List, Set
from utils.logger import Logger

logger = Logger()

class WebtoonListManager:
    """웹툰 리스트를 관리하는 클래스"""

    def __init__(self, filename: str):
        self.filename = filename
        self.urls: Set[str] = set()

    def load_urls_from_txt(self) -> bool:
        """텍스트 파일에서 웹툰 URL을 로드"""
        try:
            if not os.path.exists(self.filename):
                logger.log("info", f"{self.filename} 파일이 존재하지 않습니다.")
                return False

            with open(self.filename, "r", encoding="utf-8") as file:
                loaded_urls = {line.strip() for line in file if line.strip()}
            
            if not loaded_urls:
                logger.log("warning", f"{self.filename} 파일이 비어있습니다.")
                return False

            self.urls.update(loaded_urls)
            logger.log("info", f"텍스트 파일에서 {len(loaded_urls)}개의 URL을 로드했습니다.")
            return True

        except Exception as e:
            logger.log("error", f"URL 로드 중 오류 발생: {e}")
            return False

    def save_urls_to_txt(self) -> None:
        """수집된 웹툰 URL을 텍스트 파일에 저장"""
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                for url in sorted(self.urls):
                    file.write(f"{url}\n")
            logger.log("info", f"총 {len(self.urls)}개의 웹툰 URL을 '{self.filename}'에 저장 완료")
        except Exception as e:
            logger.log("error", f"웹툰 URL 저장 오류: {e}")

    def collect_webtoon_urls(self, list_scraper) -> None:
        """네이버 웹툰 요일별 페이지에서 모든 웹툰 URL을 수집"""
        for page_url in list_scraper.NAVER_WEBTOON_URLS:
            logger.log("info", f"웹툰 리스트 크롤링 시작: {page_url}")
            webtoon_urls = list_scraper.get_webtoon_urls(page_url)
            self.urls.update(webtoon_urls)
        
        self.save_urls_to_txt() 