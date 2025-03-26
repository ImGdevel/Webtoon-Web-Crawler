import os
import json
from typing import List
from logger import Logger

logger = Logger()

class WebtoonRepository:
    """웹툰 데이터를 JSON 파일로 저장하고 불러오는 클래스"""

    def __init__(self, success_filename: str, failure_filename: str):
        self.success_filename = success_filename
        self.failure_filename = failure_filename

    def load_existing_data(self, filename: str) -> List[dict]:
        """기존 데이터를 로드하는 메서드"""
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.log("warning", f"파일 {filename}이 비어있거나 올바르지 않은 JSON 형식입니다.")
                return []
        return []

    def append_success(self, data_list: List[dict]) -> None:
        """성공한 데이터를 JSON 파일에 추가"""
        try:
            existing_data = self.load_existing_data(self.success_filename)
            existing_ids = {item['external_id'] for item in existing_data}
            new_data = [item for item in data_list if item['external_id'] not in existing_ids]
            
            if new_data:
                existing_data.extend(new_data)
                with open(self.success_filename, "w", encoding="utf-8") as f:
                    json.dump(
                        existing_data,
                        f,
                        ensure_ascii=False,
                        separators=(',', ':'),
                        indent=2
                    )
                logger.log("info", f"{len(new_data)}개의 성공 데이터 추가 완료")
        except Exception as e:
            logger.log("error", f"성공 데이터 저장 실패: {e}")

    def append_failure(self, data_list: List[dict]) -> None:
        """실패한 데이터를 JSON 파일에 추가"""
        try:
            existing_data = self.load_existing_data(self.failure_filename)
            existing_urls = {item['url'] for item in existing_data}
            new_data = [item for item in data_list if item['url'] not in existing_urls]
            
            if new_data:
                existing_data.extend(new_data)
                with open(self.failure_filename, "w", encoding="utf-8") as f:
                    json.dump(
                        existing_data,
                        f,
                        ensure_ascii=False,
                        separators=(',', ':'),
                        indent=2 
                    )
                logger.log("info", f"{len(new_data)}개의 실패 데이터 추가 완료")
        except Exception as e:
            logger.log("error", f"실패 데이터 저장 실패: {e}")
