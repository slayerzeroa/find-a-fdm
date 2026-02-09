FROM python:3.12.4

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

# cron + timezone
RUN apt-get update \
 && apt-get install -y --no-install-recommends tzdata cron \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# /etc/cron.d 형식: "분 시 일 월 요일 사용자 명령"
# 로그를 컨테이너 stdout/stderr로 보내서 docker logs로 확인 가능
RUN printf "SHELL=/bin/bash\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\nTZ=Asia/Seoul\n0 8 * * * root cd /app && /usr/local/bin/python /app/main.py >> /proc/1/fd/1 2>> /proc/1/fd/2\n" > /etc/cron.d/wvjob \
 && chmod 0644 /etc/cron.d/wvjob \
 && crontab /etc/cron.d/wvjob

# cron foreground
CMD ["cron", "-f"]
