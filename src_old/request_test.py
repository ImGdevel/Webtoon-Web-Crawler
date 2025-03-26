import json
from dataclasses import dataclass, asdict
from typing import List
import requests
from bs4 import BeautifulSoup

@dataclass
class WebtoonDTO:
    id: int
    title: str
    link: str
    summary: str = None  # 요약 추가

@dataclass
class UpdateRequest:
    type: str
    platform: str
    list: List[WebtoonDTO]

@dataclass
class UpdateResponse:
    updated_list: List[WebtoonDTO]

SUMMARY_CLASS = 'EpisodeListInfo__summary_wrap--ZWNW5'

def fetch_summary(link: str) -> str:
    """
    링크에서 웹툰 요약 정보를 추출.
    """
    try:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        summary = soup.find('div', {'class': SUMMARY_CLASS}).find('p').text.strip()
        return summary
    except Exception as e:
        return f"Failed to fetch summary: {e}"

def update_webtoon_titles(update_request: UpdateRequest) -> UpdateResponse:
    """
    WebtoonDTO 리스트의 title에 platform을 추가하고 summary를 추가.
    """
    updated_list = []
    for webtoon in update_request.list:
        summary = fetch_summary(webtoon.link)  # 요약 크롤링
        updated_list.append(WebtoonDTO(
            id=webtoon.id,
            title=f"{update_request.platform} {webtoon.title}",
            link=webtoon.link,
            summary=summary  # 요약 추가
        ))
    return UpdateResponse(updated_list=updated_list)

def lambda_handler(event, context):
    try:
        # 요청 데이터 파싱
        body = json.loads(event["body"])
        update_request = UpdateRequest(
            type=body["type"],
            platform=body["platform"],
            list=[WebtoonDTO(**dto) for dto in body["list"]]
        )
        
        # 처리 로직 호출
        update_response = update_webtoon_titles(update_request)

        # 성공 응답 반환
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Request processed successfully.",
                "data": [asdict(dto) for dto in update_response.updated_list],
            }),
        }
    except Exception as e:
        # 에러 처리
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error processing the request.",
                "error": str(e)
            }),
        }
