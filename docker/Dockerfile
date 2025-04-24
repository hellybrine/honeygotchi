FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libatlas-base-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p config && \
    if [ ! -f config/server.key ]; then \
        ssh-keygen -t rsa -b 2048 -f config/server.key -N ""; \
    fi

RUN mkdir -p logs rl_agent/policies

CMD ["python", "main.py"]