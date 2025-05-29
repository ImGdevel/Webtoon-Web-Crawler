import json
import boto3
import requests
import os
from typing import Dict, Any, List
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory
from modules.webtoon_repository import WebtoonRepository

# AWS 클라이언트 초기화
ssm = boto3.client('ssm')
sqs = boto3.client('sqs')

# 캐시 저장소
cached_parameters = {}

def get_parameter_cached(parameter_name: str) -> str:
    """SSM 파라미터를 캐시하여 조회"""
    if parameter_name not in cached_parameters:
        try:
            response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
            cached_parameters[parameter_name] = response['Parameter']['Value']
        except Exception as e:
            raise RuntimeError(f"SSM 파라미터 조회 실패: {parameter_name} - {e}")
    return cached_parameters[parameter_name]

def lambda_handler(event, context):
    try:
        # 환경 변수 초기화
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
            "webdriver_ok": False
        }

        try:
            message_body = json.loads(record['body'])
            result["request_id"] = message_body.get('request_id')
            urls = message_body.get('requests', [])
            action = message_body.get('request_action', 'test')

            if not urls:
                raise ValueError("URL 목록이 비어있습니다.")

            try:
                # 크롤러 초기화 및 실행
                crawler = WebtoonCrawlerFactory.create_crawler(task_name=action)
                crawler.initialize(urls)
                crawler.run()
                
                # 결과 저장
                success_data, failed_data = crawler.get_results()
                
                result["updated_count"] = len(success_data)
                result["webdriver_ok"] = True

                # 성공한 웹툰 데이터를 SQS로 전송
                send_each_webtoon_to_sqs(result["request_id"], success_data, OUTPUT_SQS_URL)

            except Exception as e:
                print(f"크롤링 중 오류 발생: {e}")
                result["webdriver_ok"] = False
                raise

        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"Processing Error: {e}"
            print(result["error"])

        try:
            # 처리된 메시지 삭제
            receipt_handle = record['receiptHandle']
            delete_message_from_sqs(receipt_handle, INPUT_SQS_URL)
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"SQS Delete Error: {e}"
            print(result["error"])

        # Slack에 결과 전송
        send_slack_message(result, SLACK_WEBHOOK_URL)

    return {"statusCode": 200, "body": json.dumps("Processing complete.")}

def send_each_webtoon_to_sqs(request_id: str, webtoons: List[dict], queue_url: str) -> None:
    """각 웹툰 데이터를 SQS로 전송"""
    for webtoon in webtoons:
        try:
            message_body = {
                "request_id": request_id,
                "webtoon_data": webtoon
            }
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body)
            )
            print("SQS 메시지 전송 완료:", response['MessageId'])
        except Exception as e:
            raise RuntimeError(f"SQS 메시지 전송 실패: {e}")

def delete_message_from_sqs(receipt_handle: str, queue_url: str) -> None:
    """처리된 SQS 메시지 삭제"""
    try:
        response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        print(f"SQS 메시지 삭제 완료: {receipt_handle}")
    except Exception as e:
        raise RuntimeError(f"SQS 메시지 삭제 실패: {e}")

def send_slack_message(result: Dict[str, Any], webhook_url: str) -> None:
    """Slack으로 처리 결과 전송"""
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
