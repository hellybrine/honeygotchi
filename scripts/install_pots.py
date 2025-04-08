import os
import subprocess

def clone_repo(name, url, target_dir):
    if not os.path.exists(target_dir):
        print(f"[+] Cloning {name}...")
        subprocess.run(["git", "clone", url, target_dir])
    else:
        print(f"[=] {name} already exists.")

def install_dependencies(name, path, commands):
    print(f"[~] Installing dependencies for {name}...")
    for cmd in commands:
        subprocess.run(cmd, cwd=path, shell=True)

def main():
    # Cowrie
    cowrie_dir = "services/cowrie"
    clone_repo("Cowrie", "https://github.com/cowrie/cowrie.git", cowrie_dir)
    install_dependencies("Cowrie", cowrie_dir, [
        "python3 -m venv cowrie-env",
        "source cowrie-env/bin/activate && pip install -r requirements.txt"
    ])

    # Dionaea
    dionaea_dir = "services/dionaea"
    clone_repo("Dionaea", "https://github.com/DinoTools/dionaea.git", dionaea_dir)
    print("[!] Dionaea may require apt packages and cmake build — skip for now or handle later.")

    # Honeyd (requires manual install on most systems)
    print("[!] Honeyd requires apt install: `sudo apt install honeyd`")

if __name__ == "__main__":
    main()
