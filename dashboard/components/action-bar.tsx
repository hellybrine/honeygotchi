import { cn } from '@/lib/utils';

const ACTION_STYLES: Record<string, string> = {
  ALLOW: 'bg-emerald-500',
  DELAY: 'bg-sky-500',
  FAKE: 'bg-amber-500',
  INSULT: 'bg-fuchsia-500',
  BLOCK: 'bg-rose-500',
};

export function ActionBar({ actions }: { actions: Record<string, number> }) {
  const entries = Object.entries(actions);
  const total = entries.reduce((acc, [, v]) => acc + v, 0);
  if (total === 0) {
    return (
      <div className="text-sm text-muted-foreground">No actions recorded yet.</div>
    );
  }
  return (
    <div className="space-y-3">
      <div className="flex h-2 w-full overflow-hidden rounded-full bg-muted">
        {entries.map(([action, count]) => (
          <div
            key={action}
            className={cn('h-full', ACTION_STYLES[action] ?? 'bg-muted-foreground')}
            style={{ width: `${(count / total) * 100}%` }}
            title={`${action}: ${count}`}
          />
        ))}
      </div>
      <dl className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        {entries.map(([action, count]) => (
          <div key={action} className="flex items-baseline gap-2">
            <span
              className={cn('inline-block h-2 w-2 rounded-full', ACTION_STYLES[action] ?? 'bg-muted-foreground')}
            />
            <dt className="text-xs text-muted-foreground">{action}</dt>
            <dd className="ml-auto font-mono text-xs tabular-nums">{count}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
