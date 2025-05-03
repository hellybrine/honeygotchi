# Honeygotchi: The Playful, Adaptive SSH Honeypot Powered by Machine Learning

> _“Why just catch attackers when you can amuse, confuse, and outsmart them?”_

Welcome to **Honeygotchi**; your interactive, pet-inspired SSH honeypot that doesn’t just log attacks, but *plays* with them. Designed for defenders, researchers, and tinkerers, Honeygotchi blends deception, data science, and a dash of personality to turn your network into an intelligent trap for cyber adversaries.

---

## Key Features at a Glance

- **Lifelike SSH Emulation:** Mimics a real SSH server using Paramiko, complete with fake credentials and a playful shell.
- **Dynamic Terminal Faces:** Animated ASCII faces react in real time to attacker actions — happy, angry, bored, or just plain mischievous.
- **Humorous, Misleading Replies:** Confuse attackers with witty, bogus system responses and fake directory contents.
- **Comprehensive Command Logging:** Every command is captured and stored for forensic analysis and threat intelligence.
- **Live Stats Dashboard:** Track connections, unique IPs, and command counts right from your terminal.
- **Machine Learning Intelligence:** (Coming Soon!) Random Forest models will classify attack types — brute force, reconnaissance, script-kiddie, or advanced exploits.
- **Reinforcement Learning Roadmap:** Honeygotchi will soon adapt its behavior based on attacker interactions, getting smarter with every probe.
- **Tribute to Pwnagotchi:** Inspired by the beloved Pwnagotchi, Honeygotchi brings personality and learning to the world of honeypots.

---

## How It Works

| Component              | Description                                                                                       |
|------------------------|---------------------------------------------------------------------------------------------------|
| SSH Honeypot           | Emulates a vulnerable SSH server, engaging attackers with a convincing shell and fake credentials |
| Command Logger         | Captures every command and logs to file for later analysis                                        |
| Dynamic Faces & Stats  | ASCII faces and live stats update based on attacker behavior                                      |
| Machine Learning Core  | (Planned) Random Forest model classifies attack types in real time                                |
| Reinforcement Learning | (Planned) Adapts honeypot responses dynamically to attacker strategies                            |

---

## Installation

Honeygotchi is designed for quick and painless setup. The `install.sh` script takes care of everything; dependencies, environment, and configuration.


1. Clone the repository:
    ```bash
    git clone https://github.com/hellybrine/honeygotchi.git
    cd honeygotchi
    ```

2. Make the `install.sh` script executable:
    ```bash
    chmod +x install.sh
    ```

3. Run the installation script:
    ```bash
    ./install.sh
    ```

   The script will install all the necessary dependencies and set up the environment automatically.

4. Once the installation is complete, you can start the honeypot:
    ```bash
    python3 honeypot.py
    ```


That’s it! Honeygotchi is now live, ready to greet and log your first attacker.

---

## Live Demo

- Watch Honeygotchi’s face change as attackers connect and interact.
- See real-time stats update as new IPs and commands roll in.
- Laugh at the creative, misleading responses that keep attackers guessing.

---

## Machine Learning (Coming Soon)

Honeygotchi’s ML core will use a **Random Forest** classifier (trained on the IoT-23 dataset) to automatically categorize attacks:

- Brute-force attempts  
- Reconnaissance/scanning  
- Script-kiddie tools  
- Sophisticated exploits  

Long-term, reinforcement learning will enable Honeygotchi to evolve its responses, making it a moving target for adversaries.

---

## Roadmap

- [x] SSH emulation with humorous responses  
- [x] Dynamic ASCII faces & live stats  
- [x] Machine learning attack classification  
- [ ] Reinforcement learning for adaptive deception  
- [ ] Web UI for visualization and management  
- [ ] Simulation of additional system types (IoT, routers, etc.)

---

## Credits & Inspiration

- **Pwnagotchi:** For the idea of a pet honeypot with personality and learning
- **[Abhyudyasangwan](https://github.com/abhyudyasangwan):** Machine learning design and implementation
- **[Collinsmc23](https://github.com/collinsmc23):** Foundational SSH honeypot implementation

---

## Contributing

Want to help Honeygotchi evolve? Fork, code, and submit a PR. Ideas, bug reports, and feature requests are always welcome.

---

## License

MIT License. Use, modify, and share the fun.

---

> “In the world of honeypots, Honeygotchi is the one that smiles back.”  

---

**Note:** For security research and educational use only. Deploy responsibly.
