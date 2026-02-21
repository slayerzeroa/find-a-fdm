# # 가져올 이미지를 정의
# FROM node:20
# # 경로 설정하기
# WORKDIR /app
# # package.json 워킹 디렉토리에 복사 (.은 설정한 워킹 디렉토리를 뜻함)
# COPY package.json .

# # 명령어 실행 (의존성 설치)
# RUN npm install
# # 현재 디렉토리의 모든 파일을 도커 컨테이너의 워킹 디렉토리에 복사한다.
# COPY . .

# # 각각의 명령어들은 한줄 한줄씩 캐싱되어 실행된다.
# # package.json의 내용은 자주 바뀌진 않을 거지만
# # 소스 코드는 자주 바뀌는데
# # npm install과 COPY . . 를 동시에 수행하면
# # 소스 코드가 조금 달라질때도 항상 npm install을 수행해서 리소스가 낭비된다.

# # 8001번 포트 노출
# EXPOSE 8001

# # npm start 스크립트 실행
# CMD ["node", "index.js"]

# # 그리고 Dockerfile로 docker 이미지를 빌드해야한다.
# # $ docker build .

# syntax=docker/dockerfile:1
FROM node:20-bookworm-slim

WORKDIR /app
ENV NODE_ENV=production

# canvas 빌드/런타임에 필요한 라이브러리
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ pkg-config \
    libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev \
 && rm -rf /var/lib/apt/lists/*

# 의존성 먼저 복사(캐시 효율)
COPY package*.json ./

# lockfile 있으면 ci, 없으면 install
RUN if [ -f package-lock.json ]; then \
      npm ci --omit=dev; \
    else \
      npm install --omit=dev; \
    fi

# 소스 복사
COPY . .

# canvas를 현재 컨테이너 환경에 맞게 재빌드
RUN npm rebuild canvas --build-from-source

EXPOSE 8001
CMD ["node", "index.js"]
