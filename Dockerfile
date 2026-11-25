# 1. 가벼운 공식 Python 3.12 슬림 이미지 사용 (Docker Hub 명시)
FROM docker.io/library/python:3.12-slim

# 2. 파이썬 환경변수 설정 (.pyc 파일 생성 방지 및 로그 즉시 출력)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. 작업 디렉터리 설정
WORKDIR /app

# 4. 의존성 명세 파일 먼저 복사 및 설치 (소스 코드 변경 시 캐시 재사용으로 빌드 속도 향상)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 소스 코드 복사
COPY ./app ./app

# 6. 보안을 위해 컨테이너 내부에서 일반 사용자(appuser) 권한으로 실행
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 7. 컨테이너 외부 노출 포트
EXPOSE 8000

# 8. Uvicorn으로 FastAPI 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
