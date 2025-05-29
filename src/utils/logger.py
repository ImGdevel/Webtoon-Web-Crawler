import logging
import traceback
import inspect
from datetime import datetime
import os
import json
from typing import Any, Dict, Optional
from enum import Enum

class LoggerType(Enum):
    LOCAL = "local"
    CLOUDWATCH = "cloudwatch"

class BaseLogger:
    """로거의 기본 클래스"""
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def get_caller_info(self) -> str:
        """호출자 정보 가져오기"""
        try:
            frame = inspect.currentframe().f_back.f_back
            class_name = frame.f_locals.get('self', None).__class__.__name__ if 'self' in frame.f_locals else 'Global'
            method_name = frame.f_code.co_name
            return f"{class_name}.{method_name}"
        except:
            return "Unknown"

    def _format_log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """로그 메시지 포맷팅 - 하위 클래스에서 구현"""
        raise NotImplementedError

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """정보 로그"""
        caller = self.get_caller_info()
        log_message = self._format_log("INFO", message, {"caller": caller, **(extra or {})})
        self.logger.info(log_message)

    def error(self, message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        """에러 로그"""
        caller = self.get_caller_info()
        error_info = {
            "caller": caller,
            "error_type": error.__class__.__name__ if error else None,
            "error_message": str(error) if error else None,
            "traceback": traceback.format_exc() if error else None,
            **(extra or {})
        }
        log_message = self._format_log("ERROR", message, error_info)
        self.logger.error(log_message)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """경고 로그"""
        caller = self.get_caller_info()
        log_message = self._format_log("WARNING", message, {"caller": caller, **(extra or {})})
        self.logger.warning(log_message)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """디버그 로그"""
        caller = self.get_caller_info()
        log_message = self._format_log("DEBUG", message, {"caller": caller, **(extra or {})})
        self.logger.debug(log_message)

class LocalLogger(BaseLogger):
    """로컬 파일 기반 로깅을 위한 클래스"""
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        super().__init__()
        os.makedirs(log_dir, exist_ok=True)
        self.log_filename = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d.log"))
        
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(self.log_filename, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            '%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(console_handler)
        
        self.logger.setLevel(log_level)

    def _format_log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """로컬 로그 포맷팅"""
        if extra:
            # extra 정보를 괄호 안에 포함
            extra_str = " | ".join(f"{k}: {v}" for k, v in extra.items() if k != "caller")
            if extra_str:
                return f"{message} ({extra_str})"
        return message

class CloudWatchLogger(BaseLogger):
    """AWS CloudWatch 로깅을 위한 클래스"""
    def __init__(self):
        super().__init__()
        # Lambda 환경에서는 기본 핸들러가 CloudWatch로 로그를 전송
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                '%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(handler)

    def _format_log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """CloudWatch 로그 포맷팅"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        if extra:
            log_data.update(extra)
        return json.dumps(log_data, ensure_ascii=False)

class LoggerFactory:
    """로거 팩토리 클래스"""
    _instance = None
    _logger = None

    @classmethod
    def get_logger(cls, logger_type: LoggerType = LoggerType.LOCAL, **kwargs) -> BaseLogger:
        """로거 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = cls()
        
        if cls._logger is None or not isinstance(cls._logger, (LocalLogger if logger_type == LoggerType.LOCAL else CloudWatchLogger)):
            if logger_type == LoggerType.LOCAL:
                cls._logger = LocalLogger(**kwargs)
            else:
                cls._logger = CloudWatchLogger()
        
        return cls._logger

    @classmethod
    def set_logger_type(cls, logger_type: LoggerType, **kwargs) -> None:
        """로거 타입 변경"""
        cls._logger = None
        cls.get_logger(logger_type, **kwargs)

# 전역 로거 인스턴스 (기본값: 로컬 로거)
logger = LoggerFactory.get_logger()
