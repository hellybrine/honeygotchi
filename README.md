# Honeygotchi: A Machine Learning-Powered Interactive SSH Honeypot

Honeygotchi is an interactive SSH honeypot designed to attract, engage, and deceive attackers while logging their activities for analysis. Inspired by the idea of a "pet" honeypot, it provides attackers with an amusing, "cute" interface, and helps defenders understand and classify attack behavior. The core idea is to create an engaging environment that not only attracts attackers but also gathers insightful data that can be used to improve detection, classification, and response to future threats.

The project leverages **machine learning** to classify attacker behavior and will eventually use reinforcement learning to adapt dynamically to attacker strategies. Honeygotchi is currently in active development and serves as a lightweight, efficient, and highly customizable solution for low-interaction honeypot setups.

## Project Overview

The project consists of several key components:

- **SSH Honeypot**: The core of Honeygotchi emulates a vulnerable SSH server that responds to SSH login attempts and commands in a way that simulates a real system. The responses are designed to be misleading or humorous to confuse attackers.
  
- **Command Logging**: Honeygotchi captures every command the attacker enters and logs it for analysis. This helps with understanding the attacker's intent, the types of tools or scripts being used, and the overall attack patterns.
  
- **Dynamic Faces & Stats**: Honeygotchi features dynamic terminal-based faces that react to the attacker's actions. These faces are inspired by the Pwnagotchi project and add an element of "personality" to the honeypot. Along with these faces, the honeypot also displays live statistics on the attacker's activity.

- **Machine Learning**: The project is designed to use machine learning (specifically, a Random Forest model) to classify attack types, such as brute-force login attempts, reconnaissance, and script-kiddie attacks. This is a planned feature and will be integrated once the dataset has been processed and the model is trained.

### Current Capabilities

Honeygotchi currently has the following features:

1. **SSH Emulation**:
   - The honeypot mimics a standard SSH server using **Paramiko**, responding to login attempts with fake credentials.
   - Once an attacker successfully connects, they are presented with a terminal shell that accepts commands.
   
2. **Humorous Responses**:
   - When attackers try to execute commands, Honeygotchi responds with humorous or misleading replies, designed to confuse them or waste their time. This includes providing fake directory contents, bogus system messages, and other playful responses.

3. **Command Logging**:
   - All the commands entered by an attacker are logged into a file for later analysis. This data is invaluable for understanding the tools, techniques, and procedures used by attackers.

4. **Dynamic Faces**:
   - Honeygotchi includes a simple text-based face that reacts to the attacker's actions. Inspired by the **Pwnagotchi** project, these faces change based on the attacker’s behavior and the overall state of the honeypot.
   - **Example Faces**:
     - **Happy face** when the system is untouched.
     - **Angry face** when an attacker tries repeated login attempts.
   
5. **Basic Stats**:
   - Honeygotchi provides real-time terminal stats, such as:
     - Number of connections
     - Number of unique IP addresses
     - Number of commands logged
     - Basic attack classification data (once machine learning is implemented)

### Planned Features

1. **Machine Learning Integration (Random Forest)**:
   - A major future feature is the integration of machine learning to classify different attack types. The system will be trained on a dataset containing labeled data of benign and malicious behavior. 
   - The model will be able to classify attacks as:
     - **Brute-force login attempts**
     - **Reconnaissance (scanning and enumeration)**
     - **Script-kiddie tools**
     - **Sophisticated exploits**
   
   - This will help defenders quickly identify the nature of an attack and respond more effectively.
   
2. **Reinforcement Learning for Dynamic Behavior**:
   - In the long term, Honeygotchi will use reinforcement learning to adapt to attacker behavior. The idea is for Honeygotchi to "learn" from each interaction, becoming more effective at capturing and classifying attacks over time.

3. **Enhanced Web Interface**:
   - Currently, Honeygotchi operates via the command line. In the future, a web UI will be introduced to visualize attack data, track real-time honeypot performance, and give users a more interactive experience.
   - The web interface will show dynamic faces, attack classifications, and detailed logs in a user-friendly format.

4. **Extended Attack Simulation**:
   - The honeypot will be enhanced to simulate different types of systems (e.g., IoT devices, routers) and expose different vulnerabilities based on the attacker’s profile. 

5. **Machine Learning Model Retraining**:
   - Once the Random Forest model is trained, it will be periodically retrained to ensure Honeygotchi remains capable of identifying the latest attack techniques and adapting to new threats.

### Machine Learning Integration

The primary goal of machine learning within Honeygotchi is to improve its ability to classify attack types. **Random Forest** will be used as the classification algorithm for now due to its simplicity and efficiency, especially on resource-constrained devices like the Raspberry Pi Zero 2.

### Current Machine Learning Implementation Status

The machine learning model is currently **not yet trained**. The dataset used for training is the **IoT-23** dataset, which contains labeled network traffic data. This data will be processed and used to train the model, which will then be used to classify different attack types in real-time.

Once the model is trained, it will classify attack types based on historical patterns observed in the attacker’s interactions. However, this feature is still under development.

### Tribute to Pwnagotchi

The dynamic terminal faces, an integral feature of Honeygotchi, are inspired by **Pwnagotchi**. The idea of a "pet" honeypot with a changing personality and faces adds a layer of engagement that makes the honeypot feel more like an interactive system rather than a static one. The idea was borrowed directly from the **Pwnagotchi** project, which uses reinforcement learning to create a dynamic personality for its honeypot.

We aim to expand on this by incorporating additional interaction, including machine learning-driven decision-making and more sophisticated user feedback loops.

---

## Credits

- **Pwnagotchi**: Inspiration for the dynamic faces and personality aspect of Honeygotchi. This project would not exist without the foundational ideas from Pwnagotchi.
- **[Abhyudyasangwan](https://github.com/abhyudyasangwan)**: For invaluable assistance with the machine learning integration, helping design the structure for future attack classification and model training.
- **[Collinsmc23](https://github.com/collinsmc23)**: For providing the base SSH honeypot implementation that laid the foundation for Honeygotchi's development.

You're absolutely right! If you're using an `install.sh` script, it should handle all the dependencies for you, so the `pip install -r requirements.txt` step would be unnecessary.

Let me revise the **Installation** section to reflect this. Here's an updated version of the README with that change:

---

## Installation

To quickly set up Honeygotchi, you can use the `install.sh` script, which will handle the installation of dependencies and prepare your system to run the honeypot.

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

The honeypot will now be running and ready to interact with attackers and logging their commands.