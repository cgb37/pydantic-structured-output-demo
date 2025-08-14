FROM python:3.12-slim-bullseye

WORKDIR /app

# Install build deps and common tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements directory first for better caching
COPY requirements/ ./requirements/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8001

CMD ["python", "-m", "quart", "run", "--host", "0.0.0.0", "--port", "8001"]
