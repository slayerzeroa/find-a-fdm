# 1. Node.js 이미지를 기반으로 설정
FROM node:14

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. package.json 및 package-lock.json 복사
COPY package.json .

# 4. 의존성 설치
RUN npm install

# 5. 필요한 Babel 플러그인 설치 (에러 방지를 위해 추가)
RUN npm install @babel/plugin-proposal-private-property-in-object --save-dev

# 6. 소스 코드 전체 복사
COPY . .

# 7. React 서버의 HOST와 PORT 설정
ENV HOST=0.0.0.0
ENV PORT=3001

# 8. 3001번 포트 노출
EXPOSE 3001

# 9. 개발 서버 시작 명령
CMD ["npm", "start"]
