"""Health check server for Honeygotchi."""
import asyncio
import logging
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health checks."""
    
    server_instance = None
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            stats = self.server_instance.stats if self.server_instance else {}
            response = {
                'status': 'running',
                'uptime_seconds': (datetime.now() - datetime.fromisoformat(stats.get('start_time', datetime.now().isoformat()))).total_seconds() if stats.get('start_time') else 0,
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

class HealthCheckServer:
    """Simple HTTP server for health checks and status."""
    
    def __init__(self, port: int = 8080):
        """Initialize health check server."""
        self.port = port
        self.httpd = None
        self.server_thread = None
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'sessions_total': 0,
            'commands_total': 0,
            'active_sessions': 0
        }
        HealthCheckHandler.server_instance = self
    
    def update_stats(self, **kwargs):
        """Update statistics."""
        self.stats.update(kwargs)
    
    async def start(self):
        """Start the health check server."""
        try:
            def run_server():
                self.httpd = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)
                self.httpd.serve_forever()
            
            self.server_thread = Thread(target=run_server, daemon=True)
            self.server_thread.start()
            logger.info(f"Health check server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise
    
    async def stop(self):
        """Stop the health check server."""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=2)
        logger.info("Health check server stopped")
