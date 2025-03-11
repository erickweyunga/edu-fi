FROM python:3.10-slim
WORKDIR /app

# Install dependencies (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code will be mounted via docker-compose volume
# No need to COPY . . here! 🚫