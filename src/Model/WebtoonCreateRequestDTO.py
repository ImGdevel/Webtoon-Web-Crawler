from dataclasses import dataclass, field
from typing import List, Optional
from .enum import AgeRating, SerializationStatus, Platform
from datetime import date

@dataclass
class AuthorDTO:
    name: str
    role: Optional[str] = None
    link: Optional[str] = None

    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'link': self.link
        }

@dataclass
class GenreDTO:
    name: str

    def to_dict(self):
        return {
            'name': self.name
        }


@dataclass
class WebtoonCreateRequestDTO:
    title: str
    external_id: str
    platform: Platform
    day_of_week: str
    thumbnail_url: str
    link: str
    age_rating: AgeRating
    description: str
    serialization_status: SerializationStatus
    episode_count: int
    platform_rating: float
    publish_start_date: date 
    last_updated_date: date 
    authors: List[AuthorDTO] = field(default_factory=list)
    genres: List[GenreDTO] = field(default_factory=list)

    def to_dict(self):
        if isinstance(self.publish_start_date, str):
            publish_start_date = self.publish_start_date
        else:
            publish_start_date = self.publish_start_date.isoformat()

        if isinstance(self.last_updated_date, str):
            last_updated_date = self.last_updated_date
        else:
            last_updated_date = self.last_updated_date.isoformat()

        return {
            'title': self.title,
            'external_id': self.external_id,
            'platform': self.platform,
            'day_of_week': self.day_of_week,
            'thumbnail_url': self.thumbnail_url,
            'link': self.link,
            'age_rating': self.age_rating,
            'description': self.description,
            'serialization_status': self.serialization_status,
            'episode_count': self.episode_count,
            'platform_rating': self.platform_rating,
            'publish_start_date': publish_start_date,
            'last_updated_date': last_updated_date,
            'authors': [author.to_dict() for author in self.authors],
            'genres': [genre.to_dict() for genre in self.genres]
        }
