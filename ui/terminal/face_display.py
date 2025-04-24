import threading
import time
from blessed import Terminal

class FaceUI:
    """Pwnagotchi-inspired terminal UI with facial expressions"""
    
    FACES = {
        'neutral': "[-.-]",
        'bored': "[-.-]",
        'alert': "[O.O]",
        'blocking': "[>.<]",
        'learning': "[^.^]",
        'happy': "[^_^]",
        'insult': "[¬_¬]",
    }
    
    def __init__(self, config):
        self.term = Terminal()
        self.config = config
        self.current_face = self.FACES['neutral']
        self.status_messages = []
        self.stats = {
            'connections': 0,
            'commands': 0,
            'blocks': 0
        }
        self.running = False
        self.thread = None
        
    def start(self):
        """Start UI thread"""
        self.running = True
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop UI thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
    def _update_loop(self):
        """Main UI update loop"""
        with self.term.fullscreen(), self.term.hidden_cursor():
            while self.running:
                self._draw_interface()
                time.sleep(0.5)
                
    def _draw_interface(self):
        """Draw the terminal interface"""
        print(self.term.clear())
        
        # Header
        print(self.term.move(0, 0) + self.term.white_on_blue(" RL Honeypot v1.0 ".center(self.term.width)))
        
        # Face (centered)
        face_pos = (self.term.height // 4, self.term.width // 2 - 3)
        print(self.term.move(*face_pos) + self.term.bold(self.current_face))
        
        # Status messages
        start_y = face_pos[0] + 3
        for i, msg in enumerate(self.status_messages[-5:]):
            print(self.term.move(start_y + i, 2) + msg)
            
        # Stats
        stats_y = self.term.height - 8
        print(self.term.move(stats_y, 2) + self.term.yellow("Statistics:"))
        print(self.term.move(stats_y + 1, 4) + f"Connections: {self.stats['connections']}")
        print(self.term.move(stats_y + 2, 4) + f"Commands: {self.stats['commands']}")
        print(self.term.move(stats_y + 3, 4) + f"Blocks: {self.stats['blocks']}")
        
        # Footer
        print(self.term.move(self.term.height - 1, 0) + 
              self.term.white_on_blue(" CTRL+C to exit ".ljust(self.term.width)))
    
    def update(self, event_type, data):
        """Update UI state based on events"""
        if event_type == 'connection':
            self.stats['connections'] += 1
            self.status_messages.append(f"{time.strftime('%H:%M:%S')} - New connection from {data['ip']}")
            self.current_face = self.FACES['alert']
            
        elif event_type == 'command':
            self.stats['commands'] += 1
            self.status_messages.append(f"{time.strftime('%H:%M:%S')} - Command: {data['command']}")
            
        elif event_type == 'action':
            action = data['action']
            if action == 'block':
                self.stats['blocks'] += 1
                self.current_face = self.FACES['blocking']
            elif action == 'allow':
                self.current_face = self.FACES['happy']
            elif action == 'insult':
                self.current_face = self.FACES['insult']
            else:
                self.current_face = self.FACES['neutral']
                
            self.status_messages.append(f"{time.strftime('%H:%M:%S')} - {action.capitalize()}: {data['command']}")
            
        # Keep the last 20 messages
        self.status_messages = self.status_messages[-20:]
