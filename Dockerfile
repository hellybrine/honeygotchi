FROM python:3.9-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs models data

RUN if [ ! -f server.key ]; then \
        ssh-keygen -t rsa -b 2048 -f server.key -N "" -C "honeygotchi-$(date +%Y%m%d)"; \
        chmod 600 server.key; \
    fi

# Expose port
EXPOSE 2223

CMD ["python3", "honeypot.py"]