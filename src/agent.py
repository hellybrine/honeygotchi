import logging
import random
import re
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

ACTIONS = ('ALLOW', 'DELAY', 'FAKE', 'INSULT', 'BLOCK')

MALICIOUS_PATTERNS: Dict[str, re.Pattern] = {
    'download': re.compile(r'\b(wget|curl|fetch)\b', re.IGNORECASE),
    'remote_shell': re.compile(r'\b(nc|netcat|ncat|socat)\b', re.IGNORECASE),
    'code_execution': re.compile(r'\b(python|perl|ruby|php|node)\b\s+-[ce]', re.IGNORECASE),
    'shell_execution': re.compile(r'\b(bash|sh|zsh|dash)\b\s+-c', re.IGNORECASE),
    'encoding': re.compile(r'\b(base64|xxd|hexdump)\b', re.IGNORECASE),
    'permissions': re.compile(r'\bchmod\b\s+(\+x|\d{3,4})', re.IGNORECASE),
    'destructive': re.compile(r'\brm\b\s+(-[rf]+|--recursive|--force)', re.IGNORECASE),
    'disk_operations': re.compile(r'\bdd\b\s+if=', re.IGNORECASE),
    'privilege_escalation': re.compile(r'\b(sudo|su)\b', re.IGNORECASE),
    'credential_access': re.compile(r'(/etc/shadow|/etc/passwd|id_rsa|\.ssh/|authorized_keys)', re.IGNORECASE),
    'process_control': re.compile(r'\b(kill|killall|pkill)\b', re.IGNORECASE),
    'persistence': re.compile(r'\b(crontab|systemctl|nohup)\b', re.IGNORECASE),
}


def classify(command: str) -> str:
    for name, pattern in MALICIOUS_PATTERNS.items():
        if pattern.search(command):
            return name
    return 'none'


def phase_of(command_count: int) -> str:
    if command_count <= 3:
        return 'early'
    if command_count <= 10:
        return 'mid'
    return 'late'


@dataclass
class Decision:
    state: str
    action: str
    timestamp: float
    command: str
    is_malicious: bool


@dataclass
class SessionTracker:
    """Per-session state for the RL loop. Holds the last decision so its reward
    can be computed once the next command arrives (engagement signal) or the
    session ends (terminal signal)."""
    command_count: int = 0
    pending: Optional[Decision] = None
    session_start: float = field(default_factory=time.time)


class QLearningAgent:
    """Contextual ε-greedy Q-learning over (pattern, phase) states.

    The state captures *what kind of command* the attacker just issued and
    *how deep* they are into the session. The reward is measured engagement:
    another command arriving soon = positive, session ending = negative.
    """

    def __init__(
        self,
        epsilon: float = 0.3,
        learning_rate: float = 0.1,
        discount: float = 0.9,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.9995,
        state_manager=None,
        rng: Optional[random.Random] = None,
    ):
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.alpha = learning_rate
        self.gamma = discount
        self.rng = rng or random.Random()
        self.state_manager = state_manager
        self.save_interval = 100

        self.q: Dict[Tuple[str, str], float] = {}
        self.action_counts: Dict[str, int] = {a: 0 for a in ACTIONS}
        self.decision_count = 0

        if state_manager:
            self._restore()

    def _restore(self):
        saved = self.state_manager.load_state()
        if not saved:
            return
        self.q = {tuple(k.split('|', 1)): v for k, v in saved.get('q', {}).items()}
        self.action_counts.update(saved.get('action_counts', {}))
        self.epsilon = saved.get('epsilon', self.epsilon)
        self.decision_count = saved.get('decision_count', 0)
        logger.info(
            "Restored RL state: %d q-entries, %d decisions, ε=%.3f",
            len(self.q), self.decision_count, self.epsilon,
        )

    def set_save_interval(self, interval: int):
        self.save_interval = max(1, interval)

    def select_action(self, command: str, session: SessionTracker) -> Tuple[str, Decision]:
        pattern = classify(command)
        state = f"{pattern}|{phase_of(session.command_count)}"

        if self.rng.random() < self.epsilon:
            action = self.rng.choice(ACTIONS)
        else:
            action = self._greedy(state, pattern)

        self.action_counts[action] += 1
        self.decision_count += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        decision = Decision(
            state=state,
            action=action,
            timestamp=time.time(),
            command=command,
            is_malicious=pattern != 'none',
        )

        if self.state_manager and self.decision_count % self.save_interval == 0:
            self.save_state()

        return action, decision

    def _greedy(self, state: str, pattern: str) -> str:
        values = [self.q.get((state, a), 0.0) for a in ACTIONS]
        best = max(values)
        if best == 0.0 and all(v == 0.0 for v in values):
            return self._warm_start(pattern)
        best_actions = [a for a, v in zip(ACTIONS, values) if v == best]
        return self.rng.choice(best_actions)

    def _warm_start(self, pattern: str) -> str:
        # Reasonable priors when we have no data yet. These aren't baked-in
        # rewards — just a better-than-uniform starting point that Q-learning
        # is free to overwrite.
        if pattern == 'none':
            return 'ALLOW'
        if pattern in ('destructive', 'disk_operations'):
            return self.rng.choice(('FAKE', 'DELAY'))
        if pattern in ('download', 'code_execution', 'shell_execution'):
            return self.rng.choice(('FAKE', 'ALLOW'))
        if pattern == 'credential_access':
            return 'FAKE'
        return self.rng.choice(('ALLOW', 'DELAY', 'FAKE'))

    def observe_next_command(self, decision: Decision, next_state: str, next_is_malicious: bool):
        """Called when another command arrives after `decision` — attacker stayed."""
        dt = time.time() - decision.timestamp
        reward = self._engagement_reward(dt, next_is_malicious)
        self._td_update(decision, next_state, reward, terminal=False)

    def observe_session_end(self, decision: Decision, commands_seen: int):
        """Called when the session ends after `decision` — attacker left."""
        # Moderate penalty; tempered if they had already engaged a lot.
        engagement_bonus = min(0.5, commands_seen * 0.02)
        reward = -1.0 + engagement_bonus
        self._td_update(decision, next_state=None, reward=reward, terminal=True)

    def _engagement_reward(self, dt_seconds: float, next_is_malicious: bool) -> float:
        if dt_seconds < 5:
            base = 1.0
        elif dt_seconds < 20:
            base = 0.6
        elif dt_seconds < 60:
            base = 0.3
        else:
            base = 0.1
        if next_is_malicious:
            base += 0.3
        return base

    def _td_update(self, decision: Decision, next_state: Optional[str], reward: float, terminal: bool):
        key = (decision.state, decision.action)
        current = self.q.get(key, 0.0)
        if terminal or next_state is None:
            target = reward
        else:
            future = max(self.q.get((next_state, a), 0.0) for a in ACTIONS)
            target = reward + self.gamma * future
        self.q[key] = current + self.alpha * (target - current)

    def policy_snapshot(self) -> Dict[str, Dict[str, float]]:
        snapshot: Dict[str, Dict[str, float]] = {}
        for (state, action), value in self.q.items():
            snapshot.setdefault(state, {})[action] = value
        return snapshot

    def stats(self) -> Dict:
        return {
            'action_counts': dict(self.action_counts),
            'epsilon': self.epsilon,
            'q_size': len(self.q),
            'decision_count': self.decision_count,
        }

    def save_state(self) -> bool:
        if not self.state_manager:
            return False
        serialized = {
            'q': {f"{s}|{a}": v for (s, a), v in self.q.items()},
            'action_counts': self.action_counts,
            'epsilon': self.epsilon,
            'decision_count': self.decision_count,
        }
        return self.state_manager.save_state(serialized)
