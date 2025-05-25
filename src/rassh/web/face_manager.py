"""Manage honeypot face expressions and moods."""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List
import structlog

logger = structlog.get_logger()


class FaceManager:
    """Manages honeypot facial expressions and moods."""
    
    def __init__(self):
        self.last_event_time = datetime.now()
        self.consecutive_attacks = 0
        self.current_mood = "sleeping"
        
        # Define face expressions
        self.faces = {
            # Happy/Excited faces
            "excited": ["[^_^]", "[^o^]", "[^▽^]", "[^◡^]"],
            "happy": ["[^_^]", "[^.^]", "[^‿^]", "[^ω^]"],
            "laughing": ["[^▾^]", "[>_<]", "[^∀^]", "[≧∇≦]"],
            "mischievous": ["[^_~]", "[^_-]", "[^‾^]", "[^_°]"],
            
            # Alert/Active faces  
            "alert": ["[o_o]", "[O_O]", "[◉_◉]", "[●_●]"],
            "focused": ["[-_-]", "[=_=]", "[≡_≡]", "[━_━]"],
            "suspicious": ["[¬_¬]", "[¬‿¬]", "[¬_-]", "[¬.¬]"],
            
            # Sleepy/Inactive faces
            "sleeping": ["[z_z]", "[zzz]", "[u_u]", "[~_~]"],
            "drowsy": ["[¬_¬]", "[=_=]", "[-.-]", "[u.u]"],
            "bored": ["[-_-]", "[=.=]", "[¬_¬]", "[._.]"],
            
            # Angry/Defensive faces
            "angry": ["[>_<]", "[x_x]", "[¬_¬]", "[>.<]"],
            "annoyed": ["[¬_¬]", "[-_-]", "[=_=]", "[¬.¬]"],
            "protective": ["[◉_◉]", "[O_O]", "[●_●]", "[⊙_⊙]"],
            
            # Special states
            "thinking": ["[o.o]", "[°_°]", "[◔_◔]", "[⊙_⊙]"],
            "confused": ["[?_?]", "[°_°]", "[◔_◔]", "[⊙.⊙]"],
            "smug": ["[^_~]", "[^‾^]", "[^_-]", "[¬‿¬]"]
        }
    
    def get_face_for_event(self, event_type: str, data: Dict[str, Any] = None) -> Tuple[str, str]:
        """Get appropriate face and mood for an event."""
        now = datetime.now()
        time_since_last = (now - self.last_event_time).total_seconds()
        
        # Update last event time
        self.last_event_time = now
        
        if event_type == "new_session":
            self.consecutive_attacks = 0
            mood = "excited" if time_since_last > 300 else "alert"  # 5 minutes
            return self._get_random_face(mood), mood
            
        elif event_type == "login_attempt":
            mood = "happy"
            return self._get_random_face(mood), mood
            
        elif event_type == "malicious_command":
            self.consecutive_attacks += 1
            if self.consecutive_attacks >= 5:
                mood = "laughing"  # Really enjoying the show
            elif self.consecutive_attacks >= 3:
                mood = "mischievous"
            else:
                mood = "excited"
            return self._get_random_face(mood), mood
            
        elif event_type == "benign_command":
            mood = "focused"
            return self._get_random_face(mood), mood
            
        elif event_type == "action_taken":
            action = data.get('action', 0) if data else 0
            if action == 4:  # BLOCK
                mood = "protective"
            elif action == 3:  # INSULT
                mood = "smug"
            elif action == 2:  # FAKE
                mood = "mischievous"
            elif action == 1:  # DELAY
                mood = "thinking"
            else:  # ALLOW
                mood = "focused"
            return self._get_random_face(mood), mood
            
        elif event_type == "session_ended":
            if self.consecutive_attacks > 0:
                mood = "smug"  # Satisfied after dealing with attacker
                self.consecutive_attacks = 0
            else:
                mood = "bored"
            return self._get_random_face(mood), mood
            
        elif event_type == "idle_check":
            if time_since_last > 1800:  # 30 minutes
                mood = "sleeping"
            elif time_since_last > 600:  # 10 minutes  
                mood = "drowsy"
            else:
                mood = "bored"
            return self._get_random_face(mood), mood
            
        elif event_type == "rl_training":
            mood = "thinking"
            return self._get_random_face(mood), mood
            
        elif event_type == "error":
            mood = "confused"
            return self._get_random_face(mood), mood
            
        else:
            # Default case
            mood = "alert"
            return self._get_random_face(mood), mood
    
    def _get_random_face(self, mood: str) -> str:
        """Get a random face for the given mood."""
        if mood in self.faces:
            return random.choice(self.faces[mood])
        return "[^_^]"  # Default face
    
    def get_mood_description(self, mood: str) -> str:
        """Get human-readable description of mood."""
        descriptions = {
            "excited": "New visitor detected!",
            "happy": "Someone's trying to log in!",
            "laughing": "This attacker is persistent!",
            "mischievous": "Time to mess with them...",
            "alert": "Monitoring for threats",
            "focused": "Analyzing commands",
            "suspicious": "Something's not right...",
            "sleeping": "No activity for a while",
            "drowsy": "Getting quiet around here",
            "bored": "Waiting for some action",
            "angry": "Under heavy attack!",
            "annoyed": "These attacks are getting old",
            "protective": "Blocking malicious activity",
            "thinking": "Processing information",
            "confused": "Something unexpected happened",
            "smug": "Successfully fooled an attacker!"
        }
        return descriptions.get(mood, "Unknown mood")