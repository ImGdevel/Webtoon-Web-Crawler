import json
from typing import Dict, Any, List
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory
from modules.aws_service import AWSService, SlackNotifier
from modules.request_validator import validate_request_message
from utils.logger import logger, LoggerFactory, LoggerType

# Lambda 환경에서는 CloudWatch 로거 사용
LoggerFactory.set_logger_type(LoggerType.CLOUDWATCH)

def lambda_handler(event, context):
    try:
        # AWS 서비스 초기화
        logger.info("Lambda 함수 초기화 시작")
        aws_service = AWSService()
        input_sqs_url = aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_REQUEST_URL')
        output_sqs_url = aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_COMPLETE_URL')
        slack_webhook_url = aws_service.get_parameter('/TOONPICK/prod/SLACK/SLACK_WEBHOOK_URL')
        slack_notifier = SlackNotifier(slack_webhook_url)
        
        # 크롤러 팩토리 초기화
        crawler_factory = WebtoonCrawlerFactory()
        logger.info("Lambda 함수 초기화 완료")
    except Exception as e:
        logger.error("초기화 중 오류 발생", error=e)
        raise

    logger.info("수신 이벤트", extra={"event": event})

    for record in event['Records']:
        result = {
            "status": "SUCCESS",
            "error": None,
            "updated_count": 0,
            "webdriver_ok": False
        }

        try:
            # 메시지 검증 및 파싱
            message_body = json.loads(record['body'])
            request = validate_request_message(message_body)
            logger.info("메시지 검증 완료", extra={"size": request.size})

            if not request.requests:
                raise ValueError("URL 목록이 비어있습니다.")

            try:
                # 크롤러 초기화 및 실행
                logger.info("크롤러 초기화 시작")
                crawler = crawler_factory.create_crawler(
                    task_name="update",
                    environment="docker_lambda"
                )
                
                # URL 목록 추출
                urls = [req.url for req in request.requests]
                crawler.initialize(urls)
                crawler.run()
                
                # 결과 저장
                success_data, failed_data = crawler.get_results()
                
                result["updated_count"] = len(success_data)
                result["webdriver_ok"] = True
                logger.info("크롤링 완료", extra={
                    "success_count": len(success_data),
                    "failed_count": len(failed_data)
                })

                # 성공한 웹툰 데이터를 SQS로 전송
                for webtoon in success_data:
                    # 원본 요청에서 해당 웹툰의 ID 찾기
                    webtoon_request = next((req for req in request.requests if req.url == webtoon['url']), None)
                    if webtoon_request:
                        message_body = {
                            "webtoon_id": webtoon_request.id,
                            "platform": webtoon_request.platform,
                            "webtoon_data": webtoon
                        }
                        aws_service.send_sqs_message(output_sqs_url, message_body)
                logger.info("SQS 메시지 전송 완료")

            except Exception as e:
                logger.error("크롤링 중 오류 발생", error=e)
                result["webdriver_ok"] = False
                raise

        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"Processing Error: {e}"
            logger.error("처리 중 오류 발생", error=e)

        try:
            # 처리된 메시지 삭제
            aws_service.delete_sqs_message(input_sqs_url, record['receiptHandle'])
            logger.info("SQS 메시지 삭제 완료")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"SQS Delete Error: {e}"
            logger.error("SQS 메시지 삭제 실패", error=e)

        # Slack에 결과 전송
        slack_notifier.send_notification(result)
        logger.info("Slack 알림 전송 완료", extra={"result": result})

    return {"statusCode": 200, "body": json.dumps("Processing complete.")}
