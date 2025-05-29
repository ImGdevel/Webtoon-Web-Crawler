import boto3
import json
import requests
from typing import Dict, Any, List

class AWSService:
    def __init__(self):
        self.ssm = boto3.client('ssm')
        self.sqs = boto3.client('sqs')
        self._cached_parameters = {}

    def get_parameter(self, parameter_name: str) -> str:
        """SSM 파라미터를 캐시하여 조회"""
        if parameter_name not in self._cached_parameters:
            try:
                response = self.ssm.get_parameter(Name=parameter_name, WithDecryption=True)
                self._cached_parameters[parameter_name] = response['Parameter']['Value']
            except Exception as e:
                raise RuntimeError(f"SSM 파라미터 조회 실패: {parameter_name} - {e}")
        return self._cached_parameters[parameter_name]

    def send_sqs_message(self, queue_url: str, message_body: Dict[str, Any]) -> None:
        """SQS 메시지 전송"""
        try:
            response = self.sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message_body)
            )
            print("SQS 메시지 전송 완료:", response['MessageId'])
        except Exception as e:
            raise RuntimeError(f"SQS 메시지 전송 실패: {e}")

    def delete_sqs_message(self, queue_url: str, receipt_handle: str) -> None:
        """SQS 메시지 삭제"""
        try:
            response = self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            print(f"SQS 메시지 삭제 완료: {receipt_handle}")
        except Exception as e:
            raise RuntimeError(f"SQS 메시지 삭제 실패: {e}")

class SlackNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_notification(self, result: Dict[str, Any]) -> None:
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
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(slack_message)
            )
            print("Slack 전송 응답 코드:", response.status_code)

        except Exception as e:
            print(f"Slack 메시지 전송 실패: {e}") 