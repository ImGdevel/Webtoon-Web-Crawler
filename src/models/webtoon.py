from dataclasses import dataclass, asdict
from typing import List, Optional
from .author import AuthorDTO
from .serialization_status import SerializationStatus

@dataclass
class WebtoonDTO:
    """웹툰 정보를 저장하는 데이터 객체"""
    url: str
    title: str
    external_id: int
    platform: str
    day_of_week: Optional[str]
    thumbnail_url: str
    link: str
    age_rating: Optional[str]
    description: str
    serialization_status: Optional[SerializationStatus]
    episode_count: Optional[int]
    authors: List[AuthorDTO]
    genres: List[str]

    def to_dict(self):
        return asdict(self) 