'use client';

import { useEffect, useRef, useState } from 'react';
import { Badge, actionVariant } from '@/components/ui/badge';
import { formatRelativeTime } from '@/lib/utils';
import type { LiveEvent } from '@/lib/api';

const MAX_ITEMS = 100;

export function LiveFeed() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const source = new EventSource('/api/events');
    source.onopen = () => setConnected(true);
    source.onerror = () => setConnected(false);
    source.onmessage = (e) => {
      try {
        const event: LiveEvent = JSON.parse(e.data);
        setEvents((prev) => [event, ...prev].slice(0, MAX_ITEMS));
      } catch {
        // ignore malformed frames
      }
    };
    return () => source.close();
  }, []);

  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between pb-3">
        <div className="text-sm font-medium">Live feed</div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span
            className={`h-2 w-2 rounded-full ${connected ? 'bg-emerald-500' : 'bg-rose-500'}`}
            aria-label={connected ? 'connected' : 'disconnected'}
          />
          {connected ? 'live' : 'disconnected'}
        </div>
      </div>
      <div
        ref={containerRef}
        className="max-h-[28rem] overflow-y-auto rounded-lg border bg-muted/20 font-mono text-xs"
      >
        {events.length === 0 ? (
          <div className="p-4 text-muted-foreground">Waiting for activity...</div>
        ) : (
          <ul className="divide-y">
            {events.map((e, i) => (
              <li key={`${e.ts}-${i}`} className="flex items-center gap-3 px-3 py-2">
                <span className="w-14 shrink-0 text-muted-foreground">
                  {formatRelativeTime(e.ts)}
                </span>
                <EventLine event={e} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function EventLine({ event }: { event: LiveEvent }) {
  if (event.type === 'command') {
    return (
      <div className="flex flex-1 items-center gap-2 overflow-hidden">
        <Badge variant={actionVariant(String(event.action))}>{String(event.action)}</Badge>
        {event.is_malicious ? (
          <Badge variant="destructive">{String(event.pattern ?? 'malicious')}</Badge>
        ) : null}
        <span className="truncate">{String(event.command)}</span>
      </div>
    );
  }
  if (event.type === 'session_start') {
    return (
      <div className="flex-1 text-emerald-400">
        session start · <span className="text-muted-foreground">{String(event.username)}@</span>
        <span>{String(event.client_ip)}</span>
      </div>
    );
  }
  if (event.type === 'session_end') {
    return (
      <div className="flex-1 text-muted-foreground">
        session end · {String(event.command_count ?? 0)} cmds · {Number(event.duration ?? 0).toFixed(1)}s
      </div>
    );
  }
  if (event.type === 'login') {
    return (
      <div className="flex-1 text-sky-400">
        login · <span className="text-muted-foreground">{String(event.username)}:{String(event.password)}</span> from{' '}
        {String(event.client_ip)}
      </div>
    );
  }
  return <div className="flex-1">{JSON.stringify(event)}</div>;
}
