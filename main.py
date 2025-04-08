from core.honeygotchi import Honeygotchi
from webui.app import start_web
from threading import Thread

def run_webui():
    app = create_app()
    app.run(host="0.0.0.0", port=8080, denug=False)

def main():

    web_thread = Thread(target=run_webui, daemon=True)
    web_thread.start()

    bot = Honeygotchi()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] Honeygotchi crashed: {e}")