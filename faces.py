import time
import os
import random

faces = {
    "sleeping": [
        "  (-.-) zZz  ",
        "  (-.-) ...  ",
        "  (-.-)     "
    ],
    "active": [
        "  (^_^)      ",
        "  (o_o)/     ",
        "  (^.^)>     "
    ],
    "under_attack": [
        "  (ò_ó) !!   ",
        "  (>_<) ⚠️   ",
        "  (ಠ_ಠ)      "
    ]
}

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_face(mode="sleeping", stats=None, repeat=3, delay=0.5):
    frames = faces.get(mode, faces["sleeping"])
    for _ in range(repeat):
        for frame in frames:
            clear_terminal()
            print(frame)
            if stats:
                print("\nStats:")
                for key, val in stats.items():
                    print(f"{key}: {val}")
            time.sleep(delay)

if __name__ == "__main__":
    dummy_stats = {
        "Logged IPs": 12,
        "Commands Captured": 49,
        "Malware Dropped": 2
    }
    show_face("under_attack", dummy_stats)
