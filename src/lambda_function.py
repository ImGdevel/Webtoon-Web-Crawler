import json
import boto3
import requests
import os
from typing import Dict, Any

def get_parameter(parameter_name: str) -> str:
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

sqs = boto3.client('sqs', region_name='ap-northeast-2')
INPUT_SQS_URL = get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_REQUEST_URL')
OUTPUT_SQS_URL = get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_COMPLETE_URL')
SLACK_WEBHOOK_URL = get_parameter('/TOONPICK/prod/SLACK/SLACK_WEBHOOK_URL')

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    for record in event['Records']:
        result = {
            "request_id": None,
            "status": "SUCCESS",
            "error": None,
            "updated_count": 0
        }

        try:
            message_body = json.loads(record['body'])
            result["request_id"] = message_body.get('requestTime')
            webtoons = message_body.get('requests', [])

            updated_webtoons = process_webtoon_updates(webtoons)
            result["updated_count"] = len(updated_webtoons)

            send_each_webtoon_to_sqs(result["request_id"], updated_webtoons)

        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"Processing Error: {e}"
            print(result["error"])

        try:
            receipt_handle = record['receiptHandle']
            delete_message_from_sqs(receipt_handle)
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"SQS Delete Error: {e}"
            print(result["error"])

        send_slack_message(result)

    return {"statusCode": 200, "body": json.dumps("Processing complete.")}

def process_webtoon_updates(webtoons):
    # 실제 업데이트 로직 구현 예정
    return webtoons

def send_each_webtoon_to_sqs(request_id, updated_webtoons):
    for webtoon in updated_webtoons:
        try:
            message_body = {
                "requestId": request_id,
                "updatedWebtoon": webtoon
            }
            response = sqs.send_message(
                QueueUrl=OUTPUT_SQS_URL,
                MessageBody=json.dumps(message_body)
            )
            print("웹툰 응답 메시지를 SQS에 전송함:", response['MessageId'])
        except Exception as e:
            raise RuntimeError(f"SQS Response Send Error: {e}")

def delete_message_from_sqs(receipt_handle):
    try:
        response = sqs.delete_message(QueueUrl=INPUT_SQS_URL, ReceiptHandle=receipt_handle)
        print(f"SQS 메시지 삭제 완료: {receipt_handle}")
    except Exception as e:
        raise RuntimeError(f"SQS Delete Error: {e}")

def send_slack_message(result):
    try:
        if result["status"] == "SUCCESS":
            text = f"[Lambda 처리 성공]\n- Request ID: `{result['request_id']}`\n- 처리된 웹툰 수: `{result['updated_count']}`"
        else:
            text = f"[Lambda 처리 실패]\n- Request ID: `{result['request_id']}`\n- 오류: `{result['error']}`"

        slack_message = {"text": text}
        response = requests.post(
            SLACK_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(slack_message)
        )
        print("Slack 응답:", response.status_code)
    except Exception as e:
        print(f"Slack 전송 오류: {e}")