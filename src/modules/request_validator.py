from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field

class WebtoonUpdateRequest(BaseModel):
    """웹툰 업데이트 요청 메시지 포맷"""
    request_id: str = Field(..., description="요청 ID")
    requests: List[str] = Field(..., description="크롤링할 웹툰 URL 목록")
    request_action: str = Field(default="test", description="요청 액션 (test, update 등)")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_123456",
                "requests": [
                    "https://comic.naver.com/webtoon/list?titleId=123456",
                    "https://comic.naver.com/webtoon/list?titleId=789012"
                ],
                "request_action": "update"
            }
        }

def validate_request_message(message_body: dict) -> WebtoonUpdateRequest:
    """SQS 메시지 본문을 검증하고 파싱"""
    try:
        return WebtoonUpdateRequest(**message_body)
    except Exception as e:
        raise ValueError(f"잘못된 메시지 포맷: {str(e)}") 