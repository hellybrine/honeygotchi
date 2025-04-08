import shutil

def check_dependencies():
    tools = ["honeyd", "cowrie", "dionaea"]
    for tool in tools:
        path = shutil.which(tool)
        if path:
            print(f"[OK] {tool} found at {path}")
        else:
            print(f"[!] {tool} not found! Please install.")

if __name__ == "__main__":
    check_dependencies()