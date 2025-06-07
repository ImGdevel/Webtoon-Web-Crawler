import json
from typing import Dict, Any
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory
from modules.aws_service import AWSService, SlackNotifier
from modules.request_validator import validate_request_message
from utils.logger import logger, LoggerFactory, LoggerType
import os

LoggerFactory.set_logger_type(LoggerType.CLOUDWATCH)

def is_local_test():
    return not os.getenv('AWS_LAMBDA_FUNCTION_NAME')

def initialize_services():
    if is_local_test():
        # 로컬 테스트 시 더미 값 사용
        aws_service = None
        input_sqs_url = "dummy_input_url"
        output_sqs_url = "dummy_output_url"
        slack_webhook_url = "dummy_webhook_url"
        slack_notifier = None
    else:
        aws_service = AWSService()
        input_sqs_url = aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_REQUEST_URL')
        output_sqs_url = aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_COMPLETE_URL')
        slack_webhook_url = aws_service.get_parameter('/TOONPICK/prod/SLACK/SLACK_WEBHOOK_URL')
        slack_notifier = SlackNotifier(slack_webhook_url)

    crawler_factory = WebtoonCrawlerFactory()
    return aws_service, slack_notifier, crawler_factory, input_sqs_url, output_sqs_url

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

def send_success_results_to_sqs(success_data: list[dict], request, aws_service: AWSService, output_sqs_url: str):
    if is_local_test():
        logger.info("로컬 테스트: SQS 메시지 전송 건너뜀")
        return

    for webtoon in success_data:
        matched_req = next((req for req in request.requests if req.url == webtoon['url']), None)
        if matched_req:
            message_body = {
                "webtoon_id": matched_req.id,
                "platform": matched_req.platform,
                "webtoon_data": webtoon
            }
            aws_service.send_sqs_message(output_sqs_url, message_body)

def handle_record(record: Dict[str, Any], aws_service: AWSService, crawler_factory: WebtoonCrawlerFactory, output_sqs_url: str) -> Dict[str, Any]:
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

        request, success_data, failed_data = run_crawling(message_body, crawler_factory)

        result["updated_count"] = len(success_data)
        result["webdriver_ok"] = True

        if not is_local_test():
            send_success_results_to_sqs(success_data, request, aws_service, output_sqs_url)
            logger.info("크롤링 및 SQS 전송 완료", extra={"success": len(success_data), "failed": len(failed_data)})
        else:
            logger.info("로컬 테스트: 크롤링 완료", extra={"success": len(success_data), "failed": len(failed_data)})

    except json.JSONDecodeError as e:
        result["status"] = "FAILED"
        result["error"] = f"JSON Parsing Error: {e}"
        logger.error("JSON 파싱 오류", error=str(e))
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = f"Processing Error: {e}"
        logger.error("레코드 처리 중 오류 발생", error=e)

    if not is_local_test():
        try:
            aws_service.delete_sqs_message(input_sqs_url, record['receiptHandle'])
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"SQS Delete Error: {e}"
            logger.error("SQS 삭제 오류", error=e)

    return result

def task_process(event, context):
    aws_service, slack_notifier, crawler_factory, input_sqs_url, output_sqs_url = initialize_services()

    results = []
    for record in event['Records']:
        result = handle_record(record, aws_service, crawler_factory, output_sqs_url)
        if not is_local_test() and slack_notifier:
            slack_notifier.send_notification(result)
        results.append(result)
    
    return results

def lambda_handler(event, context=None):
    try:
        #results = task_process(event, context)
        results = []
        return {
            "statusCode": 200,
            "body": json.dumps({"results": results})
        }
    except Exception as e:
        logger.error("Lambda 핸들러 오류", error=str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
