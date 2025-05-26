import asyncio
import asyncssh
import structlog
import uuid
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from .config import AppConfig
from .database import DatabaseManager
from .filesystem import VirtualFilesystem
from ..rl.agent import HoneypotAgent
from ..rl.environment import HoneypotEnvironment
from ..commands.base import CommandProcessor
from .constants import ActionType, global_state
from ..web.dashboard import create_dashboard_app

logger = structlog.get_logger()


class HoneypotSSHServer(asyncssh.SSHServer):
    
    def __init__(self, config: AppConfig, db_manager: DatabaseManager, rl_agent: HoneypotAgent, dashboard_app):
        self.config = config
        self.db_manager = db_manager
        self.rl_agent = rl_agent
        self.dashboard_app = dashboard_app
        self.active_sessions: Dict[str, 'HoneypotSSHServerSession'] = {}
    
    def connection_made(self, conn):
        """Called when a new connection is made."""
        client_ip = conn.get_extra_info('peername')[0]
        logger.info("New connection", client_ip=client_ip)
        
        # Notify dashboard of new connection
        self.dashboard_app.update_face("new_session", {"ip": client_ip})
    
    def connection_lost(self, exc):
        """Called when connection is lost."""
        logger.info("Connection lost", exception=str(exc) if exc else None)
    
    def begin_auth(self, username):
        """Begin authentication process."""
        return True
    
    def password_auth_supported(self):
        """Enable password authentication."""
        return True
    
    def validate_password(self, username, password):
        """Validate password (always allow for honeypot)."""
        logger.info("Login attempt", username=username, password=password)
        
        # Notify dashboard of login attempt
        self.dashboard_app.update_face("login_attempt", {
            "username": username, 
            "password": password
        })
        
        return True
    
    def session_requested(self):
        """Handle session request."""
        return HoneypotSSHServerSession(
            self.config, 
            self.db_manager, 
            self.rl_agent, 
            self.dashboard_app
        )


class HoneypotSSHServerSession(asyncssh.SSHServerSession):
    """SSH session handler for honeypot."""
    
    def __init__(self, config: AppConfig, db_manager: DatabaseManager, rl_agent: HoneypotAgent, dashboard_app):
        self.config = config
        self.db_manager = db_manager
        self.rl_agent = rl_agent
        self.dashboard_app = dashboard_app
        self.session_id = str(uuid.uuid4())
        self.client_ip = None
        self.filesystem = VirtualFilesystem(config.honeypot.filesystem_file)
        self.command_processor = CommandProcessor(db_manager, self.filesystem)
        self.start_time = datetime.now()
        
        # Session state
        self.current_directory = "/"
        self.environment = {"PS1": "$ ", "HOME": "/home/user", "USER": "user"}
        
        logger.info("New session created", session_id=self.session_id)
    
    def connection_made(self, chan):
        """Called when session connection is made."""
        self.chan = chan
        self.client_ip = chan.get_extra_info('peername')[0]
        
        # Save session to database
        with self.db_manager.get_session() as db_session:
            from .database import Session
            session_record = Session(
                id=self.session_id,
                start_time=self.start_time,
                client_ip=self.client_ip,
                client_version=str(chan.get_extra_info('client_version', 'unknown'))
            )
            db_session.add(session_record)
            db_session.commit()
        
        # Notify dashboard of new session
        self.dashboard_app.update_face("new_session", {"ip": self.client_ip})
    
    def shell_requested(self):
        """Handle shell request."""
        return True
    
    def session_started(self):
        """Called when session starts."""
        self.chan.write(f"Welcome to {self.config.honeypot.hostname}\n")
        self.chan.write(f"Last login: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}\n")
        self._send_prompt()
    
    def data_received(self, data, datatype):
        """Handle received data."""
        try:
            command = data.decode('utf-8').strip()
            if command:
                asyncio.create_task(self._process_command(command))
        except UnicodeDecodeError:
            logger.warning("Invalid UTF-8 data received", session_id=self.session_id)
    
    async def _process_command(self, command: str):
        """Process received command with dashboard updates."""
        logger.info("Command received", session_id=self.session_id, command=command)
        
        # Update global state for RL
        global_state.prev_command = global_state.current_command
        global_state.current_command = command
        
        # Get RL action
        env = HoneypotEnvironment()
        observation, _ = env.reset()
        action = self.rl_agent.predict(observation)
        global_state.rl_action = action
        
        # Notify dashboard of command type
        is_malicious = self._is_malicious_command(command)
        if is_malicious:
            self.dashboard_app.update_face("malicious_command", {"command": command})
        else:
            self.dashboard_app.update_face("benign_command", {"command": command})
        
        # Execute action
        response = await self._execute_action(action, command)
        
        # Notify dashboard of action taken
        self.dashboard_app.update_face("action_taken", {"action": action})
        
        # Send response
        if response:
            self.chan.write(response)
        
        # Save command to database
        await self._save_command(command, action)
        
        # Send new prompt
        self._send_prompt()
    
    def _is_malicious_command(self, command: str) -> bool:
        """Determine if command is potentially malicious."""
        malicious_patterns = [
            'wget', 'curl', 'nc', 'netcat', 'python -c',
            'bash -c', 'sh -c', '/tmp/', 'chmod +x',
            'base64', 'echo', 'cat >', 'dd if=', 'rm -rf',
            'killall', 'pkill', 'nohup'
        ]
        return any(pattern in command.lower() for pattern in malicious_patterns)
    
    async def _execute_action(self, action: int, command: str) -> str:
        """Execute the chosen action."""
        if action == ActionType.ALLOW:
            return await self._handle_allow(command)
        elif action == ActionType.DELAY:
            return await self._handle_delay(command)
        elif action == ActionType.FAKE:
            return await self._handle_fake(command)
        elif action == ActionType.INSULT:
            return await self._handle_insult(command)
        elif action == ActionType.BLOCK:
            return await self._handle_block(command)
        else:
            return await self._handle_allow(command)  # Default
    
    async def _handle_allow(self, command: str) -> str:
        """Handle ALLOW action."""
        return await self.command_processor.process_command(command, self.current_directory)
    
    async def _handle_delay(self, command: str) -> str:
        """Handle DELAY action."""
        await asyncio.sleep(2)  # 2 second delay
        return await self.command_processor.process_command(command, self.current_directory)
    
    async def _handle_fake(self, command: str) -> str:
        """Handle FAKE action."""
        return self.db_manager.get_fake_command_output(command)
    
    async def _handle_insult(self, command: str) -> str:
        """Handle INSULT action."""
        return self.db_manager.get_insult_message(self.client_ip)
    
    async def _handle_block(self, command: str) -> str:
        """Handle BLOCK action."""
        self.chan.write("Connection terminated.\n")
        self.chan.close()
        return ""
    
    async def _save_command(self, command: str, action: int):
        """Save command to database."""
        try:
            with self.db_manager.get_session() as db_session:
                from .database import Command
                cmd_record = Command(
                    session_id=self.session_id,
                    command=command,
                    action_taken=action,
                    reward=global_state.current_reward or 0.0
                )
                db_session.add(cmd_record)
                db_session.commit()
        except Exception as e:
            logger.error("Failed to save command", error=str(e))
    
    def _send_prompt(self):
        """Send command prompt."""
        prompt = f"{self.environment.get('USER', 'user')}@{self.config.honeypot.hostname}:{self.current_directory}$ "
        self.chan.write(prompt)
    
    def connection_lost(self, exc):
        """Handle connection lost."""
        # Update session end time
        try:
            with self.db_manager.get_session() as db_session:
                from .database import Session
                session_record = db_session.query(Session).filter_by(id=self.session_id).first()
                if session_record:
                    session_record.end_time = datetime.now()
                    db_session.commit()
        except Exception as e:
            logger.error("Failed to update session end time", error=str(e))
        
        # Notify dashboard of session end
        self.dashboard_app.update_face("session_ended", {"session_id": self.session_id})
        
        logger.info("Session ended", session_id=self.session_id)


class HoneypotServer:
    """Main honeypot server."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.db_manager = DatabaseManager(config.database)
        self.rl_agent = HoneypotAgent(config.rl)
        self.server = None
        self.dashboard_app = create_dashboard_app(self.db_manager, config)
        
        # Start idle checker for dashboard
        self._start_idle_checker()
    
    def _start_idle_checker(self):
        """Start background task to check for idle periods."""
        def idle_checker():
            import time
            while True:
                time.sleep(60)  # Check every minute
                self.dashboard_app.update_face("idle_check")
        
        idle_thread = threading.Thread(target=idle_checker)
        idle_thread.daemon = True
        idle_thread.start()
    
    async def start(self):
        """Start the honeypot server."""
        logger.info("Starting honeypot server", port=self.config.honeypot.listen_port)
        
        # Load or train RL model
        model_path = Path(self.config.honeypot.data_path) / "rl_model.zip"
        if model_path.exists():
            self.rl_agent.load(str(model_path))
            logger.info("Loaded existing RL model")
        else:
            logger.info("Training new RL model")
            self.dashboard_app.update_face("rl_training")
            self.rl_agent.train(total_timesteps=10000)
            self.rl_agent.save(str(model_path))
        
        # Start web dashboard in background
        dashboard_thread = threading.Thread(
            target=self.dashboard_app.run,
            kwargs={'host': '0.0.0.0', 'port': 8080}
        )
        dashboard_thread.daemon = True
        dashboard_thread.start()
        logger.info("Web dashboard started on port 8080")
        
        # Start SSH server
        self.server = await asyncssh.listen(
            host='0.0.0.0',
            port=self.config.honeypot.listen_port,
            server_factory=lambda: HoneypotSSHServer(
                self.config, 
                self.db_manager, 
                self.rl_agent, 
                self.dashboard_app
            ),
            server_host_keys=['ssh_host_key']
        )
        
        logger.info("Honeypot server started successfully")
    
    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Honeypot server stopped")