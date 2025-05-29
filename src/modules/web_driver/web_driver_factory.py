import os
from typing import Optional
from .driver.docker_chrome_webdriver_manager import DockerChromeWebDriverManager
from .driver.local_chrome_webdriver_manager import LocalChromeWebDriverManager
from .common.i_web_driver_manager import IWebDriverManager

class WebDriverFactory:
    """WebDriver 인스턴스를 생성하는 팩토리 클래스"""
    
    @staticmethod
    def create_driver(environment: Optional[str] = None, headless: bool = False) -> IWebDriverManager:
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