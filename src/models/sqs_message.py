from typing import TypeVar, Generic, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class SQSEventType(Enum):
    WEBTOON_UPDATE = "WEBTOON_UPDATE"
    # 필요한 이벤트 타입 추가

T = TypeVar('T')

@dataclass
class SQSRequestMessage(Generic[T]):
    requestId: str
    eventType: SQSEventType
    data: T
    message: Optional[str] = None
    requestTime: int = int(datetime.now().timestamp() * 1000)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            requestId=data.get('requestId'),
            eventType=SQSEventType(data.get('eventType')),
            data=data.get('data'),
            message=data.get('message'),
            requestTime=data.get('requestTime', int(datetime.now().timestamp() * 1000))
        )

@dataclass
class WebtoonUpdateRequest:
    id: str
    platform: str
    url: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            platform=data.get('platform'),
            url=data.get('url')
        )

@dataclass
class WebtoonUpdateData:
    requests: list[WebtoonUpdateRequest]

    @classmethod
    def from_dict(cls, data: dict):
        requests = [WebtoonUpdateRequest.from_dict(req) for req in data.get('requests', [])]
        return cls(requests=requests) 