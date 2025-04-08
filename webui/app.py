from flask import Flask, render_template
from services.bait_manager import BaitManager
from ui.face import Face
from core.logger import Logger
from core.brain import Brain

app = Flask(__name__)

logger = Logger()
face = Face()
brain = Brain()
bait_manager = BaitManager(logger)

@app.route("/")
def index():
    stats = logger.collect_stats()
    reward = brain.evaluate(stats)
    current_face = face.get_face(reward)
    active_services = bait_manager.get_active_services()

    return render_template("index.html",
                           face=current_face,
                           active_services=active_services,
                           stats=stats,
                           reward=reward)

def start_web():
    app.run(host="0.0.0.0", port=5000)