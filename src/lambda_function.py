import json
import boto3

# SQS 클라이언트 설정
sqs = boto3.client('sqs', region_name='ap-northeast-2')
INPUT_SQS_URL = "https://sqs.ap-northeast-2.amazonaws.com/794038251153/SQS-TOONPICK-webtoon-update-request"
OUTPUT_SQS_URL = "https://sqs.ap-northeast-2.amazonaws.com/794038251153/SQS-TOONPICK-webtoon-update-response"

def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    for record in event['Records']:
        message_body = json.loads(record['body'])
        request_id = message_body.get('requestId')
        webtoons = message_body.get('webtoons', [])

        # 웹툰 정보 업데이트 로직
        updated_webtoons = process_webtoon_updates(webtoons)

        # SQS로 전송 비활성화
        # response_data = {
        #     "requestId": request_id,
        #     "updatedWebtoons": updated_webtoons
        # }
        # send_message_to_sqs(response_data)

        # 메시지 삭제 (처리 후) - 입력 SQS URL 사용
        receipt_handle = record['receiptHandle']
        delete_message_from_sqs(receipt_handle)

    return {"statusCode": 200, "body": json.dumps("Processing complete!!!")}


def process_webtoon_updates(webtoons):
    """ 웹툰 업데이트 로직 """
    for webtoon in webtoons:
        webtoon['lastUpdatedDate'] = '2025-03-28'
    return webtoons


def send_message_to_sqs(response_data):
    """ Lambda에서 SQS로 결과 메시지를 전송하는 함수 - 비활성화됨 """
    try:
        response_json = json.dumps(response_data)
        # 비활성화
        # response = sqs.send_message(QueueUrl=OUTPUT_SQS_URL, MessageBody=response_json)
        print(f"(비활성화) Sent response to SQS: {response_json}")
    except Exception as e:
        print(f"Error sending message to SQS: {e}")
        raise e


def delete_message_from_sqs(receipt_handle):
    """ 입력 SQS 메시지 삭제 """
    try:
        print(f"Attempting to delete message with receipt handle: {receipt_handle}")
        response = sqs.delete_message(QueueUrl=INPUT_SQS_URL, ReceiptHandle=receipt_handle)
        print(f"Message deleted from SQS, ReceiptHandle: {receipt_handle}")
    except sqs.exceptions.ReceiptHandleIsInvalid as e:
        print(f"Invalid receipt handle: {receipt_handle}. The message might have already been deleted.")
    except Exception as e:
        print(f"Error deleting message from SQS: {e}")
        raise e
