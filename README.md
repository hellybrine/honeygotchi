# Honeygotchi

A SSH honeypot that leverages multi-objective reinforcement learning to adaptively deceive attackers while maximizing intelligence collection. This system goes beyond traditional honeypots by learning optimal response strategies in real-time, maintaining extended attacker engagement through intelligent deception.

## Core Idea

Traditional honeypots face a fundamental trade-off: engage attackers long enough to gather intelligence without revealing the deception. This project solves that challenge through a PyTorch-based reinforcement learning agent that dynamically balances four competing objectives:

- **Engagement Optimization**: Keeping attackers interested and active
- **Deception Management**: Revealing convincing fake data without detection
- **Security Response**: Containing threats while maintaining the illusion
- **Intelligence Collection**: Maximizing behavioral data and attack pattern capture

## Architecture

### Multi-Objective RL Agent

The system employs four specialized neural networks, each optimizing a distinct objective:

```
State Vector (15 dimensions)    → [Engagement Net] → Action Probabilities
                                → [Deception Net] → Action Probabilities  
                                → [Security Net]  → Action Probabilities
                                → [Collection Net]→ Action Probabilities
```

**State Features**: Command complexity, session duration, attack patterns, timing analysis, privilege escalation attempts, and behavioral fingerprints.

**Action Space**: 20 discrete actions across four categories, enabling fine-grained response control.

### Adaptive Deception Engine

The deception engine generates contextually appropriate fake environments based on attacker skill classification:

- **Beginner Attackers**: Simple fake files, obvious vulnerabilities
- **Intermediate Attackers**: Encrypted files, moderate complexity systems  
- **Advanced Attackers**: Sophisticated fake infrastructure, realistic network topologies

### Realistic Content Generation

The system dynamically generates believable fake data:

- **Database Dumps**: Complete MySQL schemas with realistic user tables and hashed passwords
- **Configuration Files**: Production-like JSON configs with database credentials and API keys
- **SSH Keys**: Properly formatted RSA private keys and server credentials
- **System Files**: Authentic-looking bash histories, password files, and network configurations

## Performance Metrics

Based on extensive testing with 1000 simulated attack sessions:

- **100% fake file access success rate**: Every attacker who accessed fake sensitive files received convincing content
- **99.2% deception trigger rate**: Nearly all sessions activated deception mechanisms
- **12+ minute average session duration**: Significantly higher than typical honeypot engagement
- **33.9% data collection efficiency**: High-quality behavioral intelligence gathered

## Technical Implementation

### Session Tracking and Analysis

```python
class SessionTracker:
    def __init__(self, client_ip):
        self.session_data = {
            'commands': [],
            'file_access_attempts': 0,
            'malware_downloads': 0,
            'privilege_escalation_attempts': 0,
            'command_complexity_score': 0,
            # ... 15 additional behavioral metrics
        }
```

### Threat Assessment

Real-time threat scoring based on:
- Malware download attempts (weight: 4x)
- Data exfiltration activities (weight: 5x) 
- Privilege escalation attempts (weight: 3x)
- Network reconnaissance (weight: 2x)

### Response Planning

Intelligent blocking decisions that factor in session intelligence value:
- High-value sessions: Reduced blocking probability to extend engagement
- Low-value sessions: Standard security response protocols
- Critical threats: Immediate containment with session termination

## Installation and Setup

### Prerequisites

- Python 3.8+
- Ubuntu/Debian/CentOS Linux
- Root privileges (for SSH server binding)

### Quick Start

```bash
git clone https://github.com/hellybrine/honeygotchi.git
cd honeygotchi
chmod +x install.sh
./install.sh
```

The installation script automatically:
- Creates Python virtual environment
- Installs PyTorch and dependencies
- Generates SSH server keys
- Initializes logging and model directories

### Manual Configuration

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 honeypot.py
```

Default configuration runs on port 2223. Modify `honeypot.py` for custom ports or network interfaces.

## Model Training and Export

### Continuous Learning

The system employs experience replay with a 10,000-sample memory buffer. Training occurs automatically during operation:

```python
# Automatic training every 64 interactions
if len(self.rl_agent.memory) > 64:
    self.rl_agent.replay()
    self.stats["RL Training Episodes"] += 1
```

### Production Deployment

Export optimized models for production environments:

```python
honeypot.export_models()
```

Generates TorchScript models for faster inference:
- `engagement_net.pt`
- `deception_net.pt`
- `security_net.pt`
- `collection_net.pt`

### Data Analysis

Session data exports to CSV for threat intelligence analysis:

```python
honeypot.data_collector.export_to_csv()
```

## Advanced Features

### Behavioral Fingerprinting

The system analyzes attacker behavior patterns:
- Command timing intervals
- Tool sophistication assessment
- Error recovery strategies
- Persistence mechanisms

### Dynamic Banner Generation

Realistic SSH banners that mimic common server configurations:
- Ubuntu production servers
- CentOS enterprise systems
- Debian web servers

### Pwnagotchi-Style Interface

Clean ASCII status display with real-time metrics:
```
┌─────────────────────────────────────────────┐
│                 (◕‿‿◕)                       │
├─────────────────────────────────────────────┤
│              HONEYPOT STATUS                │
├─────────────────────────────────────────────┤
│ Active Sessions        2                    │
│ Commands Captured      1,247                │
│ RL Training Episodes   45                   │
└─────────────────────────────────────────────┘
```

## File Structure

```
honeygotchi/
├── honeypot.py              # Main server implementation
├── rl_agent.py              # Multi-objective RL agent
├── deception_engine.py      # Adaptive fake content generation
├── banner.py                # Realistic SSH banners
├── faces.py                 # Status display interface
├── model.py                 # Model management utilities
├── test.py                  # Model validation scripts
├── install.sh               # Automated setup
├── requirements.txt         # Python dependencies
├── models/                  # Trained model storage
├── data/                    # Session logs and datasets
└── logs/                    # Connection and command logs
```

## Security Considerations

This honeypot is designed for research and threat intelligence purposes. Deploy only in isolated environments:

- Use dedicated VMs or containers
- Implement network segmentation
- Monitor resource consumption during training
- Regular model and data backups
- Review logs for actual threats

## Contributing

Contributions welcome in areas of:
- Novel deception strategies
- Additional RL algorithms
- Behavioral analysis improvements
- Performance optimizations

## License

MIT License - See LICENSE file for details.

---

**Note**: This honeypot is for educational and research purposes. Ensure compliance with local laws and organizational policies before deployment.