import requests
import json

url = 'http://localhost:8080/api/webtoon-request'
headers = {
    'Content-Type': 'application/json'
}

# JSON 파일을 읽어들입니다
with open('naver_webtoon_list.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 데이터를 POST 요청으로 전송합니다
response = requests.post(url, json=data, headers=headers)

# 결과를 확인합니다
if response.status_code == 200:
    print("Success!")
    print("Response JSON:", response.json())
else:
    print("Failed to send data")
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
