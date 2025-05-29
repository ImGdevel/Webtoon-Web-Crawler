import json
import requests

# 웹툰 데이터 로드
with open("webtoon_data.json", "r", encoding="utf-8") as file:
    webtoon_data = json.load(file)

# API 엔드포인트 설정
base_url = "http://ec2-13-125-26-84.ap-northeast-2.compute.amazonaws.com:8080"
end_pint = "/api/admin/webtoons"
request_url = base_url + end_pint

# POST 요청 전송 (headers 없이도 가능)
response = requests.post(request_url, json=webtoon_data)

# 응답 출력
print(f"Status Code: {response.status_code}")
print("Response Body:", response.json())
