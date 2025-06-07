import json
from typing import Dict, Any
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory
from modules.aws_service import AWSService, SlackNotifier
from modules.request_validator import validate_request_message
from utils.logger import logger, LoggerFactory, LoggerType
import os

# 환경 설정
IS_LOCAL = True  # 로컬 테스트 환경 설정

class ServiceManager:
    def __init__(self):
        self.aws_service = None
        self.slack_notifier = None
        self.input_sqs_url = None
        self.output_sqs_url = None

    def initialize(self):
        if not IS_LOCAL:
            try:
                self.aws_service = AWSService()
                self.input_sqs_url = self.aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_REQUEST_URL')
                self.output_sqs_url = self.aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_COMPLETE_URL')
                slack_webhook_url = self.aws_service.get_parameter('/TOONPICK/prod/SLACK/SLACK_WEBHOOK_URL')
                self.slack_notifier = SlackNotifier(slack_webhook_url)
                logger.info("외부 서비스 초기화 완료")
            except Exception as e:
                logger.error(f"외부 서비스 초기화 실패: {str(e)}")
        else:
            logger.info("로컬 환경: 외부 서비스 비활성화")

    def send_to_sqs(self, message: Dict):
        if not IS_LOCAL and self.aws_service and self.output_sqs_url:
            try:
                self.aws_service.send_sqs_message(self.output_sqs_url, message)
                logger.info("SQS 메시지 전송 완료")
            except Exception as e:
                logger.error(f"SQS 메시지 전송 실패: {str(e)}")
        else:
            logger.info("로컬 환경: SQS 메시지 전송 건너뜀")

    def delete_from_sqs(self, receipt_handle: str):
        if not IS_LOCAL and self.aws_service and self.input_sqs_url:
            try:
                self.aws_service.delete_sqs_message(self.input_sqs_url, receipt_handle)
                logger.info("SQS 메시지 삭제 완료")
            except Exception as e:
                logger.error(f"SQS 메시지 삭제 실패: {str(e)}")
        else:
            logger.info("로컬 환경: SQS 메시지 삭제 건너뜀")

    def send_slack_notification(self, message: Dict):
        if not IS_LOCAL and self.slack_notifier:
            try:
                self.slack_notifier.send_notification(message)
                logger.info("Slack 알림 전송 완료")
            except Exception as e:
                logger.error(f"Slack 알림 전송 실패: {str(e)}")
        else:
            logger.info("로컬 환경: Slack 알림 전송 건너뜀")

service_manager = ServiceManager()

def run_crawling(message_body: Dict[str, Any], crawler_factory: WebtoonCrawlerFactory):
    request = validate_request_message(message_body)

    if not request.requests:
        raise ValueError("URL 목록이 비어있습니다.")

    urls = [req.url for req in request.requests]

    crawler = crawler_factory.create_crawler(
        task_name="update",
        environment="docker_lambda"
    )
    crawler.initialize(urls)
    crawler.run()

    success_data, failed_data = crawler.get_results()
    return request, success_data, failed_data

def send_success_results_to_sqs(success_data: list[dict], request):
    for webtoon in success_data:
        matched_req = next((req for req in request.requests if req.url == webtoon['url']), None)
        if matched_req:
            message_body = {
                "webtoon_id": matched_req.id,
                "platform": matched_req.platform,
                "webtoon_data": webtoon
            }
            service_manager.send_to_sqs(message_body)

def handle_record(record: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "status": "SUCCESS",
        "error": None,
        "updated_count": 0,
        "webdriver_ok": False
    }

    try:
        body = record['body']
        if isinstance(body, str):
            message_body = json.loads(body)
        else:
            message_body = body

        crawler_factory = WebtoonCrawlerFactory()
        request, success_data, failed_data = run_crawling(message_body, crawler_factory)

        result["updated_count"] = len(success_data)
        result["webdriver_ok"] = True
        result["success_data"] = success_data
        result["failed_data"] = failed_data

        # SQS 메시지 전송
        send_success_results_to_sqs(success_data, request)
        
        # SQS 메시지 삭제
        if 'receiptHandle' in record:
            service_manager.delete_from_sqs(record['receiptHandle'])

        logger.info("크롤링 완료", extra={
            "success": len(success_data), 
            "failed": len(failed_data)
        })

    except json.JSONDecodeError as e:
        result["status"] = "FAILED"
        result["error"] = f"JSON Parsing Error: {e}"
        logger.error("JSON 파싱 오류", error=str(e))
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = f"Processing Error: {e}"
        logger.error("레코드 처리 중 오류 발생", error=e)

    return result

def lambda_handler(event, context=None):
    try:
        # 서비스 초기화
        service_manager.initialize()

        results = []
        for record in event.get('Records', []):
            result = handle_record(record)
            # Slack 알림 전송
            service_manager.send_slack_notification(result)
            results.append(result)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "results": results,
                "environment": "local" if IS_LOCAL else "production"
            })
        }
    except Exception as e:
        logger.error("Lambda 핸들러 오류", error=str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
