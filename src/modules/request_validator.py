from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class WebtoonRequest(BaseModel):
    """개별 웹툰 요청 정보"""
    id: int = Field(..., description="웹툰 ID")
    platform: str = Field(..., description="플랫폼 (NAVER 등)")
    url: str = Field(..., description="웹툰 URL")

class WebtoonUpdateRequest(BaseModel):
    """웹툰 업데이트 요청 메시지 포맷"""
    size: int = Field(..., description="요청된 웹툰 개수")
    requests: List[WebtoonRequest] = Field(..., description="크롤링할 웹툰 정보 목록")
    requestTime: Optional[datetime] = Field(None, description="요청 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "size": 2,
                "requests": [
                    {
                        "id": 217,
                        "platform": "NAVER",
                        "url": "https://comic.naver.com/webtoon/list?titleId=835736"
                    },
                    {
                        "id": 218,
                        "platform": "NAVER",
                        "url": "https://comic.naver.com/webtoon/list?titleId=823026"
                    }
                ],
                "requestTime": "2024-05-29T21:36:05.323007"
            }
        }

def validate_request_message(message_body: dict) -> WebtoonUpdateRequest:
    """SQS 메시지 본문을 검증하고 파싱"""
    try:
        return WebtoonUpdateRequest(**message_body)
    except Exception as e:
        raise ValueError(f"잘못된 메시지 포맷: {str(e)}") 