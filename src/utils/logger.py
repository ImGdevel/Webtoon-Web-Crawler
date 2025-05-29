import logging
import traceback
import inspect
from datetime import datetime
import os

class Logger:
    """로그를 관리하는 클래스"""
    def __init__(
        self,
        log_dir="logs",
        log_level_console=logging.INFO,
        log_level_file=logging.DEBUG,
        enable_caller_info=False
    ):
        os.makedirs(log_dir, exist_ok=True)
        self.log_filename = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d.log"))
        self.log_level_console = log_level_console
        self.log_level_file = log_level_file
        self.enable_caller_info = enable_caller_info

        logging.basicConfig(
            filename=self.log_filename,
            level=self.log_level_file,
            format='%(asctime)s [%(levelname)-7s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'
        )

    def get_caller_info(self):
        if not self.enable_caller_info:
            return ""
        frame = inspect.currentframe().f_back.f_back
        class_name = frame.f_locals.get('self', None).__class__.__name__ if 'self' in frame.f_locals else 'Global'
        method_name = frame.f_code.co_name
        return f"[{class_name}.{method_name}] "

    def log(self, level, message):
        caller_info = self.get_caller_info()
        log_message = f"{caller_info}{message}"

        if level.lower() == "error":
            log_message += "\n" + traceback.format_exc()
        
        if logging.getLevelName(level.upper()) >= self.log_level_console:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level.upper():7s}] {log_message}")
        
        getattr(logging, level.lower())(log_message)

logger = Logger(log_dir="logs")
