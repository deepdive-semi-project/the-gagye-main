# 1단계: 빌드용 베이스 이미지 (의존성 설치)
FROM python:3.11-slim AS builder

WORKDIR /app

# 시스템 패키지 설치 (DB 연결 등을 위해 필요)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 라이브러리 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


# 2단계: 실행용 최종 이미지 (경량화)
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/install/bin:$PATH"

WORKDIR /app

# 빌드 단계에서 설치된 라이브러리만 복사
COPY --from=builder /install /usr/local

# 프로젝트 소스 복사
COPY . .

# 정적 파일 모으기 (S3를 사용하지 않는 경우 컨테이너 내부에 저장됨)
RUN python manage.py collectstatic --noinput

# 포트 개방
EXPOSE 8000

# Gunicorn으로 실행 (프로젝트명 'main' 기준, 본인 프로젝트에 맞게 수정 필요)
# --bind 0.0.0.0:8000은 ECS Fargate 연결을 위해 필수입니다.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main.wsgi:application"]