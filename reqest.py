import json
import requests

# 웹툰 데이터 로드
with open("webtoon_data.json", "r", encoding="utf-8") as file:
    webtoon_data = json.load(file)

# API 엔드포인트 설정
url = "http://localhost:8080/api/admin/webtoons/batch"

# HTTP 요청 헤더 (필요 시 인증 토큰 추가 가능)
headers = {
    "Content-Type": "application/json"
}

# POST 요청 전송
response = requests.post(url, headers=headers, data=json.dumps(webtoon_data))

# 응답 출력
print(f"Status Code: {response.status_code}")
print("Response Body:", response.json())
