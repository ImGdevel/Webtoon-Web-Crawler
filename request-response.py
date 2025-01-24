import requests
import json

def send_update_request():
    # Lambda API Gateway 엔드포인트 URL
    api_url = "https://abdvw9x7n9.execute-api.ap-northeast-2.amazonaws.com/lambda_test/testFunction"

    # 요청 데이터
    update_request = {
        "type": "update",
        "platform": "WebtoonPlatform",
        "list": [
            {
                "id": 1,
                "title": "Amazing Webtoon",
                "link": "https://comic.naver.com/webtoon/list?titleId=747269"
            },
            {
                "id": 2,
                "title": "Super Adventure",
                "link": "https://comic.naver.com/webtoon/list?titleId=777767"
            }
        ]
    }

    try:
        # POST 요청 보내기
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, json=update_request, headers=headers)

        # 응답 처리
        if response.status_code == 200:
            # 성공적으로 처리된 경우
            response_data = response.json()
            print("Request processed successfully!")
            print(json.dumps(response_data, indent=2))
        else:
            # 에러가 발생한 경우
            print(f"Error occurred: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        # 네트워크 오류 처리
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    send_update_request()
