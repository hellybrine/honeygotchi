import { UPSTREAM } from '@/lib/api';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  const upstream = await fetch(`${UPSTREAM}/api/stream`, {
    cache: 'no-store',
    headers: { Accept: 'text/event-stream' },
  });
  if (!upstream.ok || !upstream.body) {
    return new Response('upstream unavailable', { status: 502 });
  }
  return new Response(upstream.body, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  });
}
