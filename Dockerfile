# 빌드 스테이지
FROM python:3.11-slim-bullseye AS builder

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치
RUN CHROMEDRIVER_VERSION="114.0.5735.90" \
    && wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

WORKDIR /build
COPY requirements.txt .
RUN pip install --target python -r requirements.txt

# Lambda 실행 환경 기반 이미지 사용
FROM public.ecr.aws/lambda/python:3.11

# Chrome 실행에 필요한 의존성
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Chrome, ChromeDriver 복사
COPY --from=builder /usr/bin/google-chrome /usr/bin/
COPY --from=builder /usr/local/bin/chromedriver /usr/local/bin/

# Chrome 실행 권한 설정
RUN chmod +x /usr/bin/google-chrome

# Python 라이브러리 복사 및 경로 설정
COPY --from=builder /build/python /opt/python
ENV PYTHONPATH=/opt/python:${PYTHONPATH}

# Lambda 환경 변수 설정
ENV LAMBDA_TASK_ROOT=/var/task
ENV LAMBDA_RUNTIME_DIR=/var/runtime

# 코드 복사
COPY src/ ${LAMBDA_TASK_ROOT}

# Lambda 핸들러 지정
CMD ["lambda_function.lambda_handler"]
