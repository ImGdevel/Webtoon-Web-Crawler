from abc import ABC, abstractmethod
from typing import Optional, Tuple
from models.webtoon import WebtoonDTO

class IWebtoonScraper(ABC):
    """웹툰 스크래퍼 인터페이스"""

    @abstractmethod
    def fetch_webtoon(self, url: str) -> Tuple[bool, Optional[WebtoonDTO]]:
        """웹툰 정보를 가져와 WebtoonDTO 객체로 반환"""
        pass 