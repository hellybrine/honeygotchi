from flask import Flask, render_template, jsonify, request
import threading
import logging

logger = logging.getLogger('web_ui')

class WebUI:
    def __init__(self, config):
        self.config = config
        self.app = Flask(__name__,
                        template_folder='templates',
                        static_folder='static')
        self.thread = None
        self.stats = {
            'connections': 0,
            'commands': [],
            'actions': {
                'allow': 0,
                'block': 0,
                'substitute': 0,
                'delay': 0,
                'insult': 0
            }
        }
        self._setup_routes()
        
    def start(self):
        """Start web server in a separate thread"""
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Web UI started on port {self.config['ui']['web_port']}")
        
    def _run_server(self):
        """Run Flask server"""
        self.app.run(
            host=self.config['ui']['web_host'],
            port=self.config['ui']['web_port'],
            debug=False,
            use_reloader=False
        )
        
    def _setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/')
        def index():
            return render_template('index.html')
            
        @self.app.route('/api/stats')
        def get_stats():
            return jsonify(self.stats)
            
        @self.app.route('/api/commands')
        def get_commands():
            return jsonify(self.stats['commands'][-50:])
    
    def update(self, event_type, data):
        """Update UI state based on events"""
        if event_type == 'connection':
            self.stats['connections'] += 1
            
        elif event_type == 'command':
            self.stats['commands'].append({
                'timestamp': data['timestamp'],
                'command': data['command'],
                'ip': data['ip']
            })
            
        elif event_type == 'action':
            action = data['action']
            self.stats['actions'][action] += 1
            
        if len(self.stats['commands']) > 100:
            self.stats['commands'] = self.stats['commands'][-100:]