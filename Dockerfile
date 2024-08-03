FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app/

# 애플리케이션 소스 복사
COPY . /app/

# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     libglib2.0-0 && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 포트 노출
EXPOSE 80

# 컨테이너 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]