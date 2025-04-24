import yaml
import logging
import signal
import os
import argparse
from honeypot.server import HoneypotServer
from rl_agent.model import RLAgent
from ui.terminal.face_display import FaceUI
from ui.web.app import WebUI
from utils.logging import setup_logging

class AgentProvider:
    """Factory class for RL agents"""
    def __init__(self, config):
        self.config = config
        self.agent = RLAgent(config)
        
    def get_agent(self):
        """Return the RL agent instance"""
        return self.agent

def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='RL Honeypot')
    parser.add_argument('-c', '--config', default='config/config.yaml',
                      help='Path to configuration file')
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    setup_logging(config['logging'])
    logger = logging.getLogger('main')
    
    agent_provider = AgentProvider(config)
    honeypot = HoneypotServer(config, agent_provider)
    
    ui_components = []
    
    if config['ui']['terminal']:
        terminal_ui = FaceUI(config)
        ui_components.append(terminal_ui)
        
    if config['ui']['web']:
        web_ui = WebUI(config)
        ui_components.append(web_ui)
    
    for ui in ui_components:
        ui.start()
    
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        honeypot.stop()
        for ui in ui_components:
            ui.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start honeypot server
    logger.info("Starting RL Honeypot...")
    honeypot.start()

if __name__ == "__main__":
    main()