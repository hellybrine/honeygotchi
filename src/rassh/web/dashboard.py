import asyncio
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import structlog
from typing import Dict, List, Any

from ..core.database import DatabaseManager
from .face_manager import FaceManager

logger = structlog.get_logger()


class DashboardApp:
    
    def __init__(self, db_manager: DatabaseManager, config):
        self.db_manager = db_manager
        self.config = config
        self.face_manager = FaceManager()
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.config['SECRET_KEY'] = 'rassh-honeypot-secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Current state
        self.current_face = "[^_^]"
        self.current_mood = "sleeping"
        self.last_activity = datetime.now()
        self.active_sessions = 0
        self.total_commands = 0
        
        self._setup_routes()
        self._setup_websocket_handlers()
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get honeypot statistics."""
            try:
                with self.db_manager.get_session() as session:
                    from ..core.database import Session, Command
                    
                    # Get session stats
                    total_sessions = session.query(Session).count()
                    active_sessions = session.query(Session).filter(
                        Session.end_time.is_(None)
                    ).count()
                    
                    # Get command stats
                    total_commands = session.query(Command).count()
                    recent_commands = session.query(Command).filter(
                        Command.timestamp >= datetime.now() - timedelta(hours=24)
                    ).count()
                    
                    # Get top IPs
                    top_ips = session.query(Session.client_ip).group_by(
                        Session.client_ip
                    ).limit(10).all()
                    
                    return jsonify({
                        'face': self.current_face,
                        'mood': self.current_mood,
                        'stats': {
                            'total_sessions': total_sessions,
                            'active_sessions': active_sessions,
                            'total_commands': total_commands,
                            'recent_commands': recent_commands,
                            'top_ips': [ip[0] for ip in top_ips if ip[0]]
                        },
                        'last_activity': self.last_activity.isoformat()
                    })
            except Exception as e:
                logger.error("Failed to get stats", error=str(e))
                return jsonify({'error': 'Failed to get stats'}), 500
        
        @self.app.route('/api/recent_activity')
        def get_recent_activity():
            """Get recent honeypot activity."""
            try:
                with self.db_manager.get_session() as session:
                    from ..core.database import Command, Session as DBSession
                    
                    # Get recent commands with session info
                    recent = session.query(Command, DBSession).join(
                        DBSession, Command.session_id == DBSession.id
                    ).order_by(Command.timestamp.desc()).limit(20).all()
                    
                    activity = []
                    for cmd, sess in recent:
                        activity.append({
                            'timestamp': cmd.timestamp.isoformat(),
                            'command': cmd.command,
                            'client_ip': sess.client_ip,
                            'action': self._get_action_name(cmd.action_taken),
                            'reward': cmd.reward or 0
                        })
                    
                    return jsonify(activity)
            except Exception as e:
                logger.error("Failed to get recent activity", error=str(e))
                return jsonify([])
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            logger.info("Dashboard client connected")
            emit('face_update', {
                'face': self.current_face,
                'mood': self.current_mood
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info("Dashboard client disconnected")
    
    def _get_action_name(self, action: int) -> str:
        """Convert action number to name."""
        actions = {
            0: "ALLOW",
            1: "DELAY", 
            2: "FAKE",
            3: "INSULT",
            4: "BLOCK"
        }
        return actions.get(action, "UNKNOWN")
    
    def update_face(self, event_type: str, data: Dict[str, Any] = None):
        """Update face based on honeypot events."""
        old_face = self.current_face
        self.current_face, self.current_mood = self.face_manager.get_face_for_event(
            event_type, data
        )
        self.last_activity = datetime.now()
        
        # Emit update to connected clients
        self.socketio.emit('face_update', {
            'face': self.current_face,
            'mood': self.current_mood,
            'event': event_type,
            'timestamp': self.last_activity.isoformat()
        })
        
        # Log face changes
        if old_face != self.current_face:
            logger.info("Face updated", 
                       old_face=old_face, 
                       new_face=self.current_face, 
                       mood=self.current_mood,
                       event=event_type)
    
    def run(self, host='0.0.0.0', port=8080):
        """Run the dashboard."""
        logger.info("Starting web dashboard", host=host, port=port)
        self.socketio.run(self.app, host=host, port=port, debug=False)


def create_dashboard_app(db_manager: DatabaseManager, config) -> DashboardApp:
    return DashboardApp(db_manager, config)