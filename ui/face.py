class Face:
    def __init__(self):
        self.expressions = {
            "sleepy": "[z_Z]   ",
            "neutral": "[._.]   ",
            "curious": "[o_o]?  ",
            "excited": "[^_^]!! ",
            "overwhelmed": "[x_x]!!!"
        }
        self.current = None

    def update(self, reward):
        if reward < 10:
            mood = "sleepy"
        elif reward < 30:
            mood = "neutral"
        elif reward < 60:
            mood = "curious"
        elif reward < 90:
            mood = "excited"
        else:
            mood = "overwhelmed"

        if mood != self.current:
            self.current = mood
            self._render(mood)

    def _render(self, mood):
        face = self.expressions.get(mood, "[._.]")
        print(f"\n[Face] {mood.upper()} {face}\n")

    def shutdown(self):
        print("[Face] Powering down... [*_*]")
