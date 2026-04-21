import asyncio
import time
from collections import Counter, deque
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Any, Deque, Dict, List, Optional


@dataclass
class SessionRecord:
    session_id: str
    client_ip: str
    username: str
    started_at: float
    ended_at: Optional[float] = None
    command_count: int = 0
    commands: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def duration(self) -> Optional[float]:
        return None if self.ended_at is None else self.ended_at - self.started_at

    def to_dict(self, include_commands: bool = True) -> Dict[str, Any]:
        data = asdict(self)
        data['duration'] = self.duration
        if not include_commands:
            data.pop('commands', None)
        return data


class StatsRegistry:
    """Thread-safe in-memory metrics + recent-event buffer for the dashboard.

    Everything lives in a single process; the dashboard reads via HTTP, so we
    don't need Prometheus or any external TSDB.
    """

    def __init__(self, max_sessions: int = 200, max_events: int = 1000):
        self._lock = Lock()
        self._max_sessions = max_sessions
        self._max_events = max_events
        self._start_time = time.time()

        self.sessions_total = 0
        self.commands_total = 0
        self.malicious_total = 0
        self.active_sessions = 0
        self.login_attempts = 0

        self.actions: Counter = Counter()
        self.patterns: Counter = Counter()
        self.commands_by_action_malicious: Counter = Counter()  # (action, is_malicious) -> count
        self.client_ips: Counter = Counter()
        self.top_usernames: Counter = Counter()

        self._sessions: Dict[str, SessionRecord] = {}
        self._session_order: Deque[str] = deque()
        self._events: Deque[Dict[str, Any]] = deque(maxlen=max_events)

        self._subscribers: List[asyncio.Queue] = []

    # --- Counters ---

    def record_login(self, client_ip: str, username: str, password: str, accepted: bool = True):
        with self._lock:
            self.login_attempts += 1
            self.top_usernames[username] += 1
            event = {
                'type': 'login',
                'ts': time.time(),
                'client_ip': client_ip,
                'username': username,
                'password': password,
                'accepted': accepted,
            }
            self._events.append(event)
        self._publish(event)

    def start_session(self, session_id: str, client_ip: str, username: str):
        rec = SessionRecord(
            session_id=session_id,
            client_ip=client_ip,
            username=username,
            started_at=time.time(),
        )
        with self._lock:
            self.sessions_total += 1
            self.active_sessions += 1
            self.client_ips[client_ip] += 1
            self._sessions[session_id] = rec
            self._session_order.append(session_id)
            while len(self._session_order) > self._max_sessions:
                old = self._session_order.popleft()
                self._sessions.pop(old, None)
            event = {
                'type': 'session_start',
                'ts': rec.started_at,
                'session_id': session_id,
                'client_ip': client_ip,
                'username': username,
            }
            self._events.append(event)
        self._publish(event)

    def record_command(
        self,
        session_id: str,
        command: str,
        action: str,
        pattern: str,
        is_malicious: bool,
    ):
        with self._lock:
            self.commands_total += 1
            self.actions[action] += 1
            if is_malicious:
                self.malicious_total += 1
                self.patterns[pattern] += 1
            self.commands_by_action_malicious[(action, bool(is_malicious))] += 1
            rec = self._sessions.get(session_id)
            if rec:
                rec.command_count += 1
                rec.commands.append({
                    'ts': time.time(),
                    'command': command,
                    'action': action,
                    'pattern': pattern,
                    'is_malicious': is_malicious,
                })
                if len(rec.commands) > 50:
                    rec.commands = rec.commands[-50:]
            event = {
                'type': 'command',
                'ts': time.time(),
                'session_id': session_id,
                'command': command,
                'action': action,
                'pattern': pattern,
                'is_malicious': is_malicious,
            }
            self._events.append(event)
        self._publish(event)

    def end_session(self, session_id: str):
        with self._lock:
            self.active_sessions = max(0, self.active_sessions - 1)
            rec = self._sessions.get(session_id)
            if rec:
                rec.ended_at = time.time()
                event = {
                    'type': 'session_end',
                    'ts': rec.ended_at,
                    'session_id': session_id,
                    'duration': rec.duration,
                    'command_count': rec.command_count,
                }
                self._events.append(event)
            else:
                event = None
        if event:
            self._publish(event)

    # --- Views ---

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'uptime_seconds': time.time() - self._start_time,
                'sessions_total': self.sessions_total,
                'active_sessions': self.active_sessions,
                'commands_total': self.commands_total,
                'malicious_total': self.malicious_total,
                'login_attempts': self.login_attempts,
                'actions': dict(self.actions),
                'patterns': dict(self.patterns),
                'top_client_ips': self.client_ips.most_common(10),
                'top_usernames': self.top_usernames.most_common(10),
            }

    def recent_sessions(self, limit: int = 50, include_commands: bool = False) -> List[Dict[str, Any]]:
        with self._lock:
            ids = list(self._session_order)[-limit:][::-1]
            return [self._sessions[i].to_dict(include_commands=include_commands) for i in ids if i in self._sessions]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            rec = self._sessions.get(session_id)
            return rec.to_dict(include_commands=True) if rec else None

    def recent_events(self, limit: int = 200) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._events)[-limit:]

    # --- Pub/sub for SSE streaming ---

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        with self._lock:
            self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def _publish(self, event: Dict[str, Any]):
        with self._lock:
            subs = list(self._subscribers)
        for q in subs:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass


# Module-level registry used across the process.
STATS = StatsRegistry()
