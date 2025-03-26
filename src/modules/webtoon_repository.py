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

    def save_success(self, data_list: List[dict]) -> None:
        """성공한 데이터를 JSON 파일로 저장"""
        try:
            with open(self.success_filename, "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=4, ensure_ascii=False)
            logger.log("info", f"성공 데이터 저장 완료: {self.success_filename}")
        except Exception as e:
            logger.log("error", f"성공 데이터 저장 실패: {e}")

    def save_failure(self, data_list: List[dict]) -> None:
        """실패한 데이터를 JSON 파일로 저장"""
        try:
            with open(self.failure_filename, "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=4, ensure_ascii=False)
            logger.log("info", f"실패 데이터 저장 완료: {self.failure_filename}")
        except Exception as e:
            logger.log("error", f"실패 데이터 저장 실패: {e}")
