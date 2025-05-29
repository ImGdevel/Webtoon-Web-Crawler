# 빌드 스테이지
FROM python:3.11-slim-bullseye as builder

# 시스템 패키지 설치 (크롬 실행에 필요한 라이브러리 포함)
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 \
    libxtst6 libxrandr2 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치
ENV CHROMEDRIVER_VERSION=114.0.5735.90
RUN wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Python 패키지 설치
WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 실행 이미지 (최종)
FROM public.ecr.aws/lambda/python:3.11

# 런타임용 라이브러리만 설치
RUN yum update -y && yum install -y \
    libX11 libXcomposite libXcursor libXdamage libXi \
    libXtst libXrandr alsa-lib atk gtk3 \
    && yum clean all

# Chrome 및 ChromeDriver 복사
COPY --from=builder /usr/bin/google-chrome /usr/bin/
COPY --from=builder /usr/local/bin/chromedriver /usr/local/bin/

# Python 라이브러리 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Lambda 환경 변수 설정
ENV LAMBDA_TASK_ROOT=/var/task
ENV LAMBDA_RUNTIME_DIR=/var/runtime
ENV PYTHONPATH=/var/task

# Chrome 실행을 위한 환경 변수
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Lambda 핸들러 코드 복사
WORKDIR ${LAMBDA_TASK_ROOT}
COPY src/ .

# 실행 권한
RUN chmod +x /usr/bin/google-chrome && chmod +x /usr/local/bin/chromedriver

# 핸들러 지정
CMD ["lambda_function.lambda_handler"]
