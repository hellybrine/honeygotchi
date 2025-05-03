import time
import os
import random
from termcolor import colored

faces = {
    "sleeping": [
        colored(" (-.-) zZz ", "cyan"),
        colored(" (-.-) ... ", "cyan"),
        colored(" (-.-) ", "cyan")
    ],
    "active": [
        colored(" (^_^) ", "green"),
        colored(" (o_o)/ ", "green"),
        colored(" (^.^)> ", "green")
    ],
    "under_attack": [
        colored(" (ò_ó) !! ", "red"),
        colored(" (>_<) ", "red"),
        colored(" (ಠ_ಠ) ", "red")
    ],
    "happy": [
        colored(" (≧◡≦) ", "yellow"),
        colored(" (✧ω✧) ", "yellow"),
        colored(" (｡♥‿♥｡) ", "yellow")
    ],
    "sad": [
        colored(" (T_T) ", "blue"),
        colored(" (ಥ﹏ಥ) ", "blue"),
        colored(" (；ω；) ", "blue")
    ]
}

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_face(mode="sleeping", stats=None, recent=None, repeat=1, delay=0.5):
    frames = faces.get(mode, faces["sleeping"])
    for _ in range(repeat):
        for frame in frames:
            clear_terminal()
            print(colored("="*40, "magenta"))
            print(colored(f" Honeygotchi Status: {mode.upper()} ", "white", "on_magenta"))
            print(colored("="*40, "magenta"))
            
            if stats:
                print(colored("\n📊 Live Stats:", "cyan", attrs=["bold"]))
                print(f"  Logged IPs: {stats['Logged IPs']}")
                print(f"  Commands: {stats['Commands Captured']}")
                print(f"  Malware Attempts: {stats['Malware Dropped']}")
                print(f"  Current Threat: {stats['Attack Type']}")
            
            if recent:
                print(colored("\n🔍 Recent Activity:", "yellow", attrs=["bold"]))
                for entry in recent[-5:]:
                    print(f"  • {entry}")
            
            print(colored("\n" + "="*40, "magenta"))
            time.sleep(delay)