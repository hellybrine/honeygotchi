from core.honeygotchi import Honeygotchi

def main():
    try:
        bot = Honeygotchi()
        bot.run()
    except Exception as e:
        print(f"[!] Honeygotchi crashed: {e}")

if __name__ == "__main__":
    main()