import argparse
import asyncio
import logging
import logging.handlers
import os
import signal
import sys

import asyncssh

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.agent import QLearningAgent  # noqa: E402
    from src.config_loader import Config  # noqa: E402
    from src.ssh_server import HoneygotchiServer, SessionRunner, ensure_host_key  # noqa: E402
    from src.state_manager import StateManager  # noqa: E402
    from src.stats_api import StatsAPIServer  # noqa: E402
else:
    from .agent import QLearningAgent
    from .config_loader import Config
    from .ssh_server import HoneygotchiServer, SessionRunner, ensure_host_key
    from .state_manager import StateManager
    from .stats_api import StatsAPIServer


def setup_logging(log_dir: str, level: str = 'INFO'):
    os.makedirs(log_dir, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

    app_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'honeygotchi.log'), maxBytes=50 * 1024 * 1024, backupCount=5,
    )
    app_handler.setFormatter(fmt)
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    root.handlers = [app_handler, stream]

    audit = logging.getLogger('honeygotchi.audit')
    audit.propagate = False
    audit_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'audit.log'), maxBytes=100 * 1024 * 1024, backupCount=10,
    )
    audit_handler.setFormatter(logging.Formatter('%(message)s'))
    audit.handlers = [audit_handler]
    audit.setLevel(logging.INFO)
    return audit


def parse_args():
    p = argparse.ArgumentParser(description='Honeygotchi - Adaptive SSH honeypot with RL')
    p.add_argument('--config', help='Path to YAML config')
    p.add_argument('--port', type=int, help='SSH port')
    p.add_argument('--host', help='SSH bind host')
    p.add_argument('--api-port', type=int, help='Stats API port (used by dashboard)')
    p.add_argument('--log-dir', help='Log directory')
    p.add_argument('--state-file', help='RL state file path')
    p.add_argument('--host-key', help='SSH host key path')
    p.add_argument('--epsilon', type=float, help='RL exploration rate')
    p.add_argument('--learning-rate', type=float, help='RL learning rate')
    p.add_argument('--clear-state', action='store_true', help='Clear saved RL state and start fresh')
    return p.parse_args()


async def run():
    args = parse_args()
    config = Config(args.config)

    for cli_key, cfg_key in [
        ('port', 'ssh.port'),
        ('host', 'ssh.host'),
        ('api_port', 'api.port'),
        ('log_dir', 'logging.log_dir'),
        ('state_file', 'reinforcement_learning.state_file'),
        ('host_key', 'ssh.host_key'),
        ('epsilon', 'reinforcement_learning.epsilon'),
        ('learning_rate', 'reinforcement_learning.learning_rate'),
    ]:
        val = getattr(args, cli_key)
        if val is not None:
            config.update(cfg_key, val)

    log_dir = config.get('logging.log_dir', 'logs')
    log_level = config.get('logging.level', 'INFO')
    audit = setup_logging(log_dir, log_level)
    logger = logging.getLogger(__name__)
    logger.info("starting Honeygotchi")

    state_file = config.get('reinforcement_learning.state_file', 'data/rl_state.json')
    state = StateManager(state_file)
    if args.clear_state:
        state.clear_state()
        logger.info("cleared saved RL state")

    agent = QLearningAgent(
        epsilon=config.get('reinforcement_learning.epsilon', 0.3),
        learning_rate=config.get('reinforcement_learning.learning_rate', 0.1),
        discount=config.get('reinforcement_learning.discount', 0.9),
        state_manager=state,
    )
    agent.set_save_interval(config.get('reinforcement_learning.save_interval', 100))

    api = StatsAPIServer(port=config.get('api.port', 8080), agent=agent)
    await api.start()

    host_key = config.get('ssh.host_key', 'data/ssh_host_key')
    ensure_host_key(host_key)

    runner = SessionRunner(agent, audit, seed_salt=os.urandom(8).hex())

    async def process_factory(process):
        await runner.run(process)

    def server_factory():
        return HoneygotchiServer(audit)

    ssh_port = config.get('ssh.port', 2222)
    ssh_host = config.get('ssh.host', '0.0.0.0')
    server = await asyncssh.listen(
        host=ssh_host,
        port=ssh_port,
        server_factory=server_factory,
        server_host_keys=[host_key],
        process_factory=process_factory,
        server_version='SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5',
    )
    logger.info("SSH honeypot listening on %s:%d", ssh_host, ssh_port)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    try:
        await stop.wait()
    finally:
        logger.info("shutting down")
        server.close()
        await server.wait_closed()
        agent.save_state()
        await api.stop()
        logger.info("shutdown complete")


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
