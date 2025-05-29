import json
import boto3
import requests
import os
from typing import Dict, Any



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import os

class LambdaChromeWebDriverManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver_path = "/opt/chromedriver"
        self.binary_path = "/opt/headless-chromium"

    def get_driver(self):
        options = Options()
        options.binary_location = self.binary_path

        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")

        options.add_argument("--single-process")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--mute-audio")

        service = Service(executable_path=self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

from typing import List, Tuple

class IWebtoonCrawler:
    def initialize_urls(self) -> None:
        pass

    def process_batch(self, url_batch: List[str]) -> Tuple[List[dict], List[dict]]:
        pass

    def run(self) -> None:
        pass


class InitWebtoonCrawler(IWebtoonCrawler):
    BATCH_SIZE = 10

    def __init__(self):
        self.driver_manager = LambdaChromeWebDriverManager(headless=True)
        self.driver = self.driver_manager.get_driver()

    def initialize_urls(self) -> None:
        pass

    def process_batch(self, url_batch: List[str]) -> Tuple[List[dict], List[dict]]:
        pass

    def run(self) -> None:
        pass


# 캐시 저장소
cached_parameters = {}
ssm = boto3.client('ssm')
sqs = boto3.client('sqs')  # region은 IAM 설정에 따름

def get_parameter_cached(parameter_name: str) -> str:
    if parameter_name not in cached_parameters:
        try:
            response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
            cached_parameters[parameter_name] = response['Parameter']['Value']
        except Exception as e:
            raise RuntimeError(f"SSM 파라미터 조회 실패: {parameter_name} - {e}")
    return cached_parameters[parameter_name]

def lambda_handler(event, context):
    try:
        INPUT_SQS_URL = get_parameter_cached('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_REQUEST_URL')
        OUTPUT_SQS_URL = get_parameter_cached('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_COMPLETE_URL')
        SLACK_WEBHOOK_URL = get_parameter_cached('/TOONPICK/prod/SLACK/SLACK_WEBHOOK_URL')
    except Exception as e:
        print(f"초기화 중 오류 발생: {e}")
        raise

    print("수신 이벤트:", json.dumps(event))

    for record in event['Records']:
        result = {
            "request_id": None,
            "status": "SUCCESS",
            "error": None,
            "updated_count": 0,
            "webdriver_ok": False  # ✅ 추가됨: WebDriver 성공 여부
        }

        try:
            message_body = json.loads(record['body'])
            result["request_id"] = message_body.get('requestTime')
            webtoons = message_body.get('requests', [])

            # ✅ WebDriver 테스트 추가
            try:
                from selenium.common.exceptions import WebDriverException
                crawler = InitWebtoonCrawler()
                driver = crawler.driver
                driver.get("https://www.google.com")
                print("WebDriver 정상 작동, 페이지 타이틀:", driver.title)
                driver.quit()
                result["webdriver_ok"] = True
            except WebDriverException as we:
                print(f"WebDriver 작동 실패: {we}")
                result["webdriver_ok"] = False
            except Exception as e:
                print(f"WebDriver 초기화 오류: {e}")
                result["webdriver_ok"] = False

            updated_webtoons = process_webtoon_updates(webtoons)
            result["updated_count"] = len(updated_webtoons)

            send_each_webtoon_to_sqs(result["request_id"], updated_webtoons, OUTPUT_SQS_URL)

        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"Processing Error: {e}"
            print(result["error"])

        try:
            receipt_handle = record['receiptHandle']
            delete_message_from_sqs(receipt_handle, INPUT_SQS_URL)
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"SQS Delete Error: {e}"
            print(result["error"])

        # ✅ WebDriver 결과 포함하여 Slack에 전송
        send_slack_message(result, SLACK_WEBHOOK_URL)

    return {"statusCode": 200, "body": json.dumps("Processing complete.")}


def process_webtoon_updates(webtoons):
    # TODO: 실제 업데이트 로직 구현 예정
    return webtoons


def send_each_webtoon_to_sqs(request_id, updated_webtoons, queue_url):
    for webtoon in updated_webtoons:
        try:
            message_body = {
                "requestId": request_id,
                "updatedWebtoon": webtoon
            }
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body)
            )
            print("SQS 메시지 전송 완료:", response['MessageId'])
        except Exception as e:
            raise RuntimeError(f"SQS 메시지 전송 실패: {e}")


def delete_message_from_sqs(receipt_handle, queue_url):
    try:
        response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        print(f"SQS 메시지 삭제 완료: {receipt_handle}")
    except Exception as e:
        raise RuntimeError(f"SQS 메시지 삭제 실패: {e}")


def send_slack_message(result, webhook_url):
    try:
        driver_status = "✅ 정상" if result.get("webdriver_ok") else "❌ 실패"
        
        if result["status"] == "SUCCESS":
            text = (
                f"[Lambda 처리 성공]\n"
                f"- Request ID: `{result['request_id']}`\n"
                f"- 처리된 웹툰 수: `{result['updated_count']}`\n"
                f"- WebDriver 상태: {driver_status}"
            )
        else:
            text = (
                f"[Lambda 처리 실패]\n"
                f"- Request ID: `{result['request_id']}`\n"
                f"- 오류: `{result['error']}`\n"
                f"- WebDriver 상태: {driver_status}"
            )

        slack_message = {"text": text}
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(slack_message)
        )
        print("Slack 전송 응답 코드:", response.status_code)

    except Exception as e:
        print(f"Slack 메시지 전송 실패: {e}")
