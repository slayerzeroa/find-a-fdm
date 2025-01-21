# Use Python base image
FROM python:3.12.4

# Install tzdata for timezone configuration
RUN apt-get update && apt-get install -y tzdata

# Set the timezone (replace 'Asia/Seoul' with your desired timezone)
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first to leverage layer caching
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default command (optional, set based on your application)
CMD ["python", "main.py"]
