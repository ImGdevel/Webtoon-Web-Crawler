import json
from typing import Dict, Any, List
from crawler.webtoon_crawler_factory import WebtoonCrawlerFactory
from modules.aws_service import AWSService, SlackNotifier
from modules.request_validator import validate_request_message

def lambda_handler(event, context):
    try:
        # AWS 서비스 초기화
        aws_service = AWSService()
        input_sqs_url = aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_REQUEST_URL')
        output_sqs_url = aws_service.get_parameter('/TOONPICK/prod/AWS/AWS_SQS_WEBTOON_UPDATE_COMPLETE_URL')
        slack_webhook_url = aws_service.get_parameter('/TOONPICK/prod/SLACK/SLACK_WEBHOOK_URL')
        slack_notifier = SlackNotifier(slack_webhook_url)
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
            # 메시지 검증 및 파싱
            message_body = json.loads(record['body'])
            request = validate_request_message(message_body)
            result["request_id"] = request.request_id

            if not request.requests:
                raise ValueError("URL 목록이 비어있습니다.")

            try:
                # 크롤러 초기화 및 실행
                crawler = WebtoonCrawlerFactory.create_crawler(task_name=request.request_action)
                crawler.initialize(request.requests)
                crawler.run()
                
                # 결과 저장
                success_data, failed_data = crawler.get_results()
                
                result["updated_count"] = len(success_data)
                result["webdriver_ok"] = True

                # 성공한 웹툰 데이터를 SQS로 전송
                for webtoon in success_data:
                    message_body = {
                        "request_id": request.request_id,
                        "webtoon_data": webtoon
                    }
                    aws_service.send_sqs_message(output_sqs_url, message_body)

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
            aws_service.delete_sqs_message(input_sqs_url, record['receiptHandle'])
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = f"SQS Delete Error: {e}"
            print(result["error"])

        # Slack에 결과 전송
        slack_notifier.send_notification(result)

    return {"statusCode": 200, "body": json.dumps("Processing complete.")}
