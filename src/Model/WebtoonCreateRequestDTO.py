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
    externalId: str
    platform: Platform
    dayOfWeek: str
    thumbnailUrl: str
    link: str
    ageRating: AgeRating
    description: str
    serializationStatus: SerializationStatus
    episodeCount: int
    platformRating: float
    publishStartDate: date
    lastUpdatedDate: date
    authors: List[AuthorDTO] = field(default_factory=list)
    genres: List[GenreDTO] = field(default_factory=list)

    def to_dict(self):
        return {
            'title': self.title,
            'externalId': self.externalId,
            'platform': self.platform.value,
            'dayOfWeek': self.dayOfWeek,
            'thumbnailUrl': self.thumbnailUrl,
            'link': self.link,
            'ageRating': self.ageRating.value,
            'description': self.description,
            'serializationStatus': self.serializationStatus.value,
            'episodeCount': self.episodeCount,
            'platformRating': self.platformRating,
            'publishStartDate': self.publishStartDate.isoformat(),
            'lastUpdatedDate': self.lastUpdatedDate.isoformat(),
            'authors': [author.to_dict() for author in self.authors],
            'genres': [genre.to_dict() for genre in self.genres]
        }