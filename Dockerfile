FROM python:3.11-slim

WORKDIR /app

ENV MPLCONFIGDIR=/tmp/matplotlib

RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/

RUN mkdir -p logs data /tmp/matplotlib

RUN ssh-keygen -t rsa -b 2048 -f ssh_host_key -N ""

EXPOSE 2222 9090

CMD ["python", "src/honeygotchi.py"]