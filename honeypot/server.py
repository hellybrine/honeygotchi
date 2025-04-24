import paramiko
import threading
import socket
import logging
from honeypot.session import Session
from utils.logging import setup_logger

logger = setup_logger('honeypot_server')

class HoneypotServer:
    def __init__(self, config, agent_provider):
        self.config = config
        self.agent_provider = agent_provider
        self.host_key = paramiko.RSAKey(filename=config['ssh']['key_path'])
        self.sock = None
        self.running = False
        
    def start(self):
        """Start SSH honeypot server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.config['ssh']['host'], self.config['ssh']['port']))
        self.sock.listen(100)
        self.running = True
        
        logger.info(f"SSH honeypot listening on port {self.config['ssh']['port']}")
        
        try:
            while self.running:
                client, addr = self.sock.accept()
                logger.info(f"Connection from {addr[0]}:{addr[1]}")
                thread = threading.Thread(target=self._handle_connection, args=(client, addr))
                thread.daemon = True
                thread.start()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Gracefully stop the server"""
        self.running = False
        if self.sock:
            self.sock.close()
        logger.info("SSH honeypot stopped")
            
    def _handle_connection(self, client_socket, addr):
        """Handle incoming SSH connection"""
        try:
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self.host_key)
            
            # Get RL agent for this session
            agent = self.agent_provider.get_agent()
            session = Session(addr[0], agent)
            
            server = SSHInterface(session)
            transport.start_server(server=server)
            
            # Process channel
            channel = transport.accept(20)
            if channel is None:
                logger.warning(f"No channel established from {addr[0]}")
                return
                
            session.handle_session(channel)
        except Exception as e:
            logger.error(f"Error handling connection from {addr[0]}: {e}")
        finally:
            client_socket.close()

class SSHInterface(paramiko.ServerInterface):
    def __init__(self, session):
        self.session = session
        
    def check_auth_password(self, username, password):
        # Always accept credentials but log them
        logger.info(f"Login attempt: {username}:{password}")
        return paramiko.AUTH_SUCCESSFUL
        
    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED
        
    def check_channel_shell_request(self, channel):
        return True