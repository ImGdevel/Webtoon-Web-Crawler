FROM public.ecr.aws/lambda/python:3.11

# 필요한 시스템 패키지 설치
RUN yum update -y && yum install -y \
    libX11 libXcomposite libXcursor libXdamage libXext libXfixes \
    libXi libXrandr libXrender libXtst libXt libXxf86vm \
    mesa-libgbm alsa-lib at-spi2-atk at-spi2-core atk cairo \
    cups-libs dbus-libs expat gtk3 libdrm libgcc libxcb libxshmfence \
    nspr nss nss-util pango unzip xorg-x11-fonts-75dpi xorg-x11-fonts-Type1 \
    fontconfig freetype redhat-lsb-core wget which chromium chromium-headless && \
    yum clean all

# ChromeDriver 설치 (Chrome 114 버전용)
RUN curl -Lo /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/bin/ && \
    rm /tmp/chromedriver.zip

# 작업 디렉토리 설정
WORKDIR /var/task

# 소스 코드 복사
COPY src/ .
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# AWS 및 Lambda 환경 변수 설정
ENV AWS_DEFAULT_REGION=ap-northeast-2
ENV AWS_ACCESS_KEY_ID=dummy-key
ENV AWS_SECRET_ACCESS_KEY=dummy-secret
ENV LAMBDA_TASK_ROOT=/var/task
ENV LAMBDA_RUNTIME_DIR=/var/runtime

# Chrome 임시 디렉토리 생성 및 권한 설정
RUN mkdir -p /tmp/chrome \
    && chmod -R 777 /tmp/chrome

# 실행 권한 설정
RUN chmod +x /usr/bin/chromium && chmod +x /usr/bin/chromedriver

# 핸들러 지정
CMD ["lambda_function.lambda_handler"]