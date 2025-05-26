# Honeygotchi: Reinforced Adaptive SSH Honeypot

Honeygotchi is a playful but serious SSH honeypot that uses reinforcement learning to mess with intruders, learn from their behavior, and give you insight into how attackers operate. It’s lightweight, modular, and made to run on humble hardware like a Raspberry Pi. Think Tamagotchi meets intrusion detection.

## Highlights

* **Adaptive Responses**: A Deep Q-Network agent decides how to react (allow, delay, fake, insult, or block) based on attacker commands.
* **Fake Filesystem**: Believable Linux environment with realistic file trees and command outputs.
* **Command Recognition**: Extracts patterns from incoming commands to help classify behavior and detect known threats.
* **ASCII Dashboard**: Terminal faces respond to intrusions in real-time so monitoring feels less like a chore.
* **Built with Love (and Python)**: Python 3.11+, AsyncSSH, SQLAlchemy, and Stable-Baselines3.
* **Tiny Footprint**: Runs fine on a Pi 3B+ without melting.
* **Easy to Deploy**: Dockerized setup with environment variables and hardening.

## Architecture

Honeygotchi is split into five main parts:

* **SSH Honeypot**: Built with AsyncSSH. Manages sessions and logs commands.
* **Reinforcement Learning Agent**: Trains a DQN model that adjusts its strategy based on real intrusions.
* **Virtual Filesystem**: Simulates a fake Linux system using serialized Pickle data.
* **Database**: SQLAlchemy ORM with MySQL backend stores session logs and agent state.
* **Web Dashboard**: Real-time updates via Flask-SocketIO, including live ASCII animations.

## Quick Start

### Requirements

* Docker and Docker Compose
* At least 2GB RAM (4GB recommended for Pi)
* SSH port 2222 open on your network

### Setup

```bash
git clone https://github.com/yourusername/honeygotchi.git
cd honeygotchi

cp .env.example .env
# Edit .env to your liking

ssh-keygen -t rsa -b 2048 -f ssh_host_key -N ""

docker-compose up -d
docker-compose logs -f honeygotchi
```

### Services

* **SSH Honeypot**: `ssh root@localhost -p 2222`
* **Dashboard**: `http://localhost:8080`
* **Database**: `localhost:3306` (check `.env` for credentials)

## Why Build This?

Most honeypots get boring fast. Once an attacker figures out your system isn’t real, they leave. Honeygotchi tries to stay interesting. It learns from interaction, reacts in weird or helpful ways, and keeps bad actors busy just a bit longer.

* **Learns from Real Activity**: The agent evolves based on what attackers actually do.
* **Better Logs, Better Insights**: Tracks commands and builds profiles based on attacker behavior.
* **Fun to Watch**: The dashboard is like a Tamagotchi that gets grumpy when poked by hackers.
* **Works on Low Power**: You don’t need a server farm to run this.

## Configuration

Edit `.env` to configure behavior:

```bash
# Database
DB_HOST=mysql
DB_USERNAME=honeygotchi
DB_PASSWORD=your_secure_password

# Honeypot
HONEYPOT_LISTEN_PORT=2222
HONEYPOT_MAX_SESSIONS=100

# RL Agent
RL_LEARNING_RATE=0.01
RL_EPSILON=0.1
RL_BATCH_SIZE=32
```

## For Developers and Tinkerers

### Local Dev Setup

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
black src/ tests/
isort src/ tests/
mypy src/
```

### Research and Experimentation

You can use Honeygotchi to:

* Analyze how attackers behave across different networks
* Test new RL algorithms and compare how they respond to threats
* Experiment with deception tactics
* Use it in class to demonstrate security principles in action

## Performance

On a Raspberry Pi 3B+:

* **Memory**: 180MB idle, up to 350MB when training
* **CPU**: 15–20% normally, spikes to 60% during training
* **Storage**: Around 500MB for the base install, more for logs
* **Latency**: \~120ms per command
* **Sessions**: Can juggle 100+ attackers
* **Training Time**: Around 12 minutes to converge over 10,000 episodes

## Security Notes

* **Container Isolation**: Runs in Docker with non-root users and restricted privileges
* **Input Filtering**: All inputs are sanitized
* **Network Controls**: Designed to run inside a segmented network
* **Data Safety**: Logs can be anonymized and encrypted if needed

## Want to Contribute?

Contributions are welcome! To get started:

1. Fork the repo and create a feature branch
2. Write your changes and include tests

### Roadmap Ideas

* Try other RL algorithms (PPO, A3C, etc)
* Improve profiling of attackers
* Plug into external threat intel feeds
* Make cloud setup easier

## License

This project is licensed under the MIT License

## Citation

```bibtex
@software{honeygotchi2025,
  title={Honeygotchi: Reinforced Adaptive SSH Honeypot},
  author={Your Name},
  year={2025},
  url={https://github.com/hellybrine/honeygotchi}
}
```

## Thanks

Honeygotchi wouldn’t exist without the RASSH and Pwnagotchi projects. Huge thanks to everyone in the security community who makes tools, datasets, and memes that inspire projects like this.

## Help and Docs

* Docs in `/docs`
* Open issues or feature requests on GitHub
* Join the discussion tab for questions and ideas
* Report security issues privately via email

---

**Honeygotchi**: a little digital pet that lives in your terminal and fights hackers for fun.
