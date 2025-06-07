import os
from typing import Optional
from .driver import (
    ChromeWebDriverManager,
    DockerChromeWebDriverManager,
    WebDriverManager
)
from .common.i_web_driver_manager import IWebDriverManager

class WebDriverFactory:
    """웹 드라이버 팩토리 클래스"""

    def create_driver(self, environment: str = "local", headless: bool = True) -> WebDriverManager:
        """
        환경에 따른 웹 드라이버 매니저를 생성합니다.

        Args:
            environment (str): 실행 환경 ("local" 또는 "docker_lambda")
            headless (bool): 헤드리스 모드 사용 여부 (로컬 환경에서만 적용)

        Returns:
            WebDriverManager: 웹 드라이버 매니저 인스턴스
        """
        if environment == "docker_lambda":
            # Docker Lambda 환경에서는 항상 headless 모드로 동작
            return DockerChromeWebDriverManager()
        else:
            # 로컬 환경에서만 headless 옵션 적용
            return ChromeWebDriverManager(headless=headless)

    @staticmethod
    def create_driver_old(environment: Optional[str] = None, headless: bool = False) -> IWebDriverManager:
        """
        환경에 맞는 WebDriver 인스턴스를 생성합니다.
        
        Args:
            environment (str, optional): 실행 환경 ("local", "lambda", "docker_lambda")
                                      None인 경우 자동으로 환경 감지
            headless (bool): 헤드리스 모드 사용 여부
            
        Returns:
            IWebDriverManager: WebDriver 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 환경이 지정된 경우
        """
        # 환경이 지정되지 않은 경우 자동 감지
        if environment is None:
            if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None:
                # Docker Lambda 환경인지 확인
                if os.path.exists('/usr/bin/google-chrome'):
                    environment = "docker_lambda"
                else:
                    environment = "lambda"
            else:
                environment = "local"

        environment = environment.lower()
        
        if environment == "local":
            return LocalChromeWebDriverManager(headless=headless)
        elif environment == "docker_lambda":
            return DockerChromeWebDriverManager(headless=headless)
        else:
            raise ValueError(f"지원하지 않는 환경입니다: {environment}") 