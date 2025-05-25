from dataclasses import dataclass, asdict
from typing import List, Optional, Set
from .author import AuthorDTO
from models.enums import SerializationStatus, Platform, AgeRating, DayOfWeek
from .enums.age_rating import AgeRating
from datetime import date

@dataclass
class WebtoonDTO:
    """웹툰 정보를 저장하는 데이터 객체"""
    title: str
    external_id: str
    platform: Platform
    day_of_week: DayOfWeek
    thumbnail_url: str
    link: str
    age_rating: AgeRating
    description: str
    serialization_status: SerializationStatus
    episode_count: int
    platform_rating: float
    publish_start_date: Optional[date]
    last_updated_date: Optional[date]
    authors: Set[AuthorDTO]
    genres: List[str]

    def to_dict(self):
        return asdict(self) 