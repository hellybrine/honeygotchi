import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from aiohttp import web

from .metrics import STATS

logger = logging.getLogger(__name__)


def _cors_headers() -> dict:
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }


@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == 'OPTIONS':
        return web.Response(status=204, headers=_cors_headers())
    response = await handler(request)
    for k, v in _cors_headers().items():
        response.headers[k] = v
    return response


class StatsAPIServer:
    """HTTP API that the dashboard consumes. Serves JSON snapshots and an SSE
    stream of live events so the UI can update without polling."""

    def __init__(self, port: int = 8080, agent=None):
        self.port = port
        self.agent = agent
        self.start_time = datetime.now()
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None

    def set_agent(self, agent):
        self.agent = agent

    async def start(self):
        app = web.Application(middlewares=[cors_middleware])
        app.router.add_get('/health', self._health)
        app.router.add_get('/api/stats', self._stats)
        app.router.add_get('/api/policy', self._policy)
        app.router.add_get('/api/sessions', self._sessions)
        app.router.add_get('/api/sessions/{sid}', self._session)
        app.router.add_get('/api/events', self._events)
        app.router.add_get('/api/stream', self._stream)

        self._runner = web.AppRunner(app, access_log=None)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, '0.0.0.0', self.port)
        await self._site.start()
        logger.info("stats API on :%d", self.port)

    async def stop(self):
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()

    async def _health(self, _request: web.Request) -> web.Response:
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
        })

    async def _stats(self, _request: web.Request) -> web.Response:
        payload = STATS.snapshot()
        payload['start_time'] = self.start_time.isoformat()
        if self.agent:
            payload['agent'] = self.agent.stats()
        return web.json_response(payload)

    async def _policy(self, _request: web.Request) -> web.Response:
        if not self.agent:
            return web.json_response({'error': 'agent not available'}, status=503)
        return web.json_response(self.agent.policy_snapshot())

    async def _sessions(self, request: web.Request) -> web.Response:
        limit = min(int(request.query.get('limit', 50)), 200)
        include = request.query.get('commands', '0') in ('1', 'true', 'yes')
        return web.json_response(STATS.recent_sessions(limit=limit, include_commands=include))

    async def _session(self, request: web.Request) -> web.Response:
        sid = request.match_info['sid']
        rec = STATS.get_session(sid)
        if not rec:
            return web.json_response({'error': 'not found'}, status=404)
        return web.json_response(rec)

    async def _events(self, request: web.Request) -> web.Response:
        limit = min(int(request.query.get('limit', 200)), 1000)
        return web.json_response(STATS.recent_events(limit=limit))

    async def _stream(self, request: web.Request) -> web.StreamResponse:
        response = web.StreamResponse(headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            **_cors_headers(),
        })
        await response.prepare(request)
        queue = STATS.subscribe()
        try:
            # Send a snapshot of recent events so the client starts with context.
            for event in STATS.recent_events(limit=25):
                await response.write(f"data: {json.dumps(event)}\n\n".encode())
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=20.0)
                    await response.write(f"data: {json.dumps(event)}\n\n".encode())
                except asyncio.TimeoutError:
                    # keep-alive ping
                    await response.write(b": ping\n\n")
        except (ConnectionResetError, asyncio.CancelledError):
            pass
        finally:
            STATS.unsubscribe(queue)
        return response
