import json
from typing import Dict, Any
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory
from modules.aws_service import AWSService, SlackNotifier
from modules.request_validator import validate_request_message
from utils.logger import logger, LoggerFactory, LoggerType

LoggerFactory.set_logger_type(LoggerType.CLOUDWATCH)


def initialize_services():
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
        message_body = json.loads(record['body'])
        request, success_data, failed_data = run_crawling(message_body, crawler_factory)

        result["updated_count"] = len(success_data)
        result["webdriver_ok"] = True

        send_success_results_to_sqs(success_data, request, aws_service, output_sqs_url)
        logger.info("크롤링 및 SQS 전송 완료", extra={"success": len(success_data), "failed": len(failed_data)})

    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = f"Processing Error: {e}"
        logger.error("레코드 처리 중 오류 발생", error=e)

    try:
        aws_service.delete_sqs_message(input_sqs_url, record['receiptHandle'])
    except Exception as e:
        result["status"] = "FAILED"
        result["error"] = f"SQS Delete Error: {e}"
        logger.error("SQS 삭제 오류", error=e)

    return result


def task_process(event, context):
    aws_service, slack_notifier, crawler_factory, input_sqs_url, output_sqs_url = initialize_services()

    for record in event['Records']:
        result = handle_record(record, aws_service, crawler_factory, output_sqs_url)
        slack_notifier.send_notification(result)


def lambda_handler(event, context):

    task_process(event, context)

    return {"statusCode": 200, "body": json.dumps("Processing complete.")}
