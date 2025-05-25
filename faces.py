import os
import time
from termcolor import colored

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

# Pwnagotchi-style faces
FACES = {
    'sleeping': "(⇀‿‿↼)",
    'active': "(◕‿‿◕)", 
    'happy': "(•‿‿•)",
    'under_attack': "(°▃▃°)",
    'angry': "(-_-')",
    'bored': "(-__-)",
    'cool': "(⌐■_■)",
    'excited': "(ᵔ◡◡ᵔ)",
    'grateful': "(^▿▿^)",
    'motivated': "(☼▿▿☼)",
    'demotivated': "(≖__≖)",
    'lonely': "(ب__ب)",
    'sad': "(╥☁╥ )",
    'friend': "(♥▿▿♥)",
    'broken': "(☓▿▿☓)",
    'debug': "(#__#)"
}

def show_face(mode, stats, recent_activity, repeat=1, delay=2):
    """Display honeypot status with pwnagotchi-style faces"""
    
    # Map modes to faces
    face_map = {
        'sleeping': 'sleeping',
        'active': 'active', 
        'happy': 'happy',
        'under_attack': 'under_attack',
        'angry': 'angry',
        'bored': 'bored'
    }
    
    face = FACES.get(face_map.get(mode, 'active'), FACES['active'])
    
    colors = {
        'sleeping': 'cyan',
        'active': 'green',
        'happy': 'yellow',
        'under_attack': 'red',
        'angry': 'magenta',
        'bored': 'blue'
    }
    
    for _ in range(repeat):
        clear_screen()
        
        # Create pwnagotchi-style display
        display_lines = [
            "┌─────────────────────────────────────────────┐",
            f"│                    {face}                    │",
            "├─────────────────────────────────────────────┤",
            "│              HONEYPOT STATUS                │",
            "├─────────────────────────────────────────────┤"
        ]
        
        # Add stats
        for key, value in stats.items():
            line = f"│ {key:<20} {str(value):<20} │"
            if key == "Attack Type" and "critical" in str(value).lower():
                display_lines.append(colored(line, 'red', attrs=['bold']))
            elif key == "Active Sessions" and value > 0:
                display_lines.append(colored(line, 'yellow', attrs=['bold']))
            elif key == "RL Training Episodes" and value > 0:
                display_lines.append(colored(line, 'green'))
            else:
                display_lines.append(line)
        
        display_lines.append("├─────────────────────────────────────────────┤")
        display_lines.append("│              RECENT ACTIVITY                │")
        display_lines.append("├─────────────────────────────────────────────┤")
        
        # Add recent activity
        if recent_activity:
            for activity in recent_activity[-5:]:
                activity_short = activity[:41] + "..." if len(activity) > 41 else activity
                line = f"│ {activity_short:<43} │"
                
                if any(keyword in activity.lower() for keyword in ['wget', 'curl', 'malware']):
                    display_lines.append(colored(line, 'red'))
                elif any(keyword in activity.lower() for keyword in ['sudo', 'su', 'passwd']):
                    display_lines.append(colored(line, 'yellow'))
                else:
                    display_lines.append(line)
        else:
            display_lines.append("│ No recent activity                         │")
        
        display_lines.append("├─────────────────────────────────────────────┤")
        display_lines.append("│ RL: Multi-objective optimization active    │")
        display_lines.append("│ Deception: Adaptive filesystem enabled     │")
        display_lines.append("│ Learning: Real-time training engaged       │")
        display_lines.append("└─────────────────────────────────────────────┘")
        
        # Display with appropriate color
        face_color = colors.get(mode, 'white')
        for line in display_lines:
            if not line.startswith(colored("", "")):  # If not already colored
                print(colored(line, face_color) if "│" in line and face in line else line)
            else:
                print(line)
        
        if delay > 0:
            time.sleep(delay)

def show_startup_banner():
    """Show startup banner without honeypot references"""
    banner = """
┌──────────────────────────────────────────────────────────────┐
│                     NETWORK SECURITY MONITOR                 │
│                                                              │
│              Advanced Threat Detection System                │
│                                                              │
│  Features:                                                   │
│  • Intelligent Response Planning                            │
│  • Adaptive Threat Assessment                               │
│  • Real-time Security Analysis                              │
│  • Behavioral Pattern Recognition                           │
│  • Automated Incident Response                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
    """
    
    print(colored(banner, 'cyan', attrs=['bold']))
    time.sleep(2)

def show_shutdown_banner():
    """Show shutdown banner"""
    banner = """
┌──────────────────────────────────────────────────────────────┐
│                    SYSTEM SHUTDOWN                           │
│                                                              │
│              Security Monitor Deactivated                    │
│                     Data Saved Successfully                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
    """
    
    print(colored(banner, 'yellow', attrs=['bold']))