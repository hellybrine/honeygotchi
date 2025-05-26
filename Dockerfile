FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/ ./src/
COPY ssh_host_key* ./

# Create directories
RUN mkdir -p logs data

# Generate SSH key if not exists
RUN if [ ! -f ssh_host_key ]; then ssh-keygen -t rsa -b 2048 -f ssh_host_key -N ""; fi

EXPOSE 2222 9090

CMD ["python", "src/honeygotchi.py"]