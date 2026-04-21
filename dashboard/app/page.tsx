import { ActionBar } from '@/components/action-bar';
import { LiveFeed } from '@/components/live-feed';
import { StatCard } from '@/components/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { fetchUpstream, type Stats } from '@/lib/api';
import { formatDuration } from '@/lib/utils';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function loadStats(): Promise<Stats | null> {
  try {
    return await fetchUpstream<Stats>('/api/stats');
  } catch {
    return null;
  }
}

export default async function Overview() {
  const stats = await loadStats();

  if (!stats) {
    return (
      <div className="rounded-lg border bg-muted/30 p-8 text-center text-muted-foreground">
        Honeypot not reachable. Make sure the <code>honeygotchi</code> container is running.
      </div>
    );
  }

  const engagement = stats.commands_total > 0
    ? ((stats.malicious_total / stats.commands_total) * 100).toFixed(1) + '%'
    : '—';

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-5">
        <StatCard label="Active sessions" value={stats.active_sessions} />
        <StatCard label="Total sessions" value={stats.sessions_total} />
        <StatCard label="Commands" value={stats.commands_total} hint={`${engagement} flagged malicious`} />
        <StatCard label="Login attempts" value={stats.login_attempts} />
        <StatCard label="Uptime" value={formatDuration(stats.uptime_seconds)} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Action distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ActionBar actions={stats.actions} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>RL agent</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {stats.agent ? (
              <>
                <Row label="Decisions" value={stats.agent.decision_count.toLocaleString()} />
                <Row label="Q-states learned" value={stats.agent.q_size.toString()} />
                <Row label="Exploration ε" value={stats.agent.epsilon.toFixed(3)} />
              </>
            ) : (
              <div className="text-sm text-muted-foreground">Agent stats unavailable.</div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Live feed</CardTitle>
          </CardHeader>
          <CardContent>
            <LiveFeed />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top attacker IPs</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.top_client_ips.length === 0 ? (
              <div className="text-sm text-muted-foreground">No sessions yet.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>IP</TableHead>
                    <TableHead className="text-right">Sessions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stats.top_client_ips.map(([ip, count]) => (
                    <TableRow key={ip}>
                      <TableCell className="font-mono text-xs">{ip}</TableCell>
                      <TableCell className="text-right font-mono tabular-nums">{count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Attack patterns detected</CardTitle>
          </CardHeader>
          <CardContent>
            <PatternTable patterns={stats.patterns} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top attempted usernames</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.top_usernames.length === 0 ? (
              <div className="text-sm text-muted-foreground">No login attempts yet.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Username</TableHead>
                    <TableHead className="text-right">Attempts</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stats.top_usernames.map(([user, count]) => (
                    <TableRow key={user}>
                      <TableCell className="font-mono text-xs">{user}</TableCell>
                      <TableCell className="text-right font-mono tabular-nums">{count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="font-mono tabular-nums">{value}</span>
    </div>
  );
}

function PatternTable({ patterns }: { patterns: Record<string, number> }) {
  const rows = Object.entries(patterns).sort((a, b) => b[1] - a[1]);
  if (rows.length === 0) {
    return <div className="text-sm text-muted-foreground">No malicious patterns detected.</div>;
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Pattern</TableHead>
          <TableHead className="text-right">Hits</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(([pattern, count]) => (
          <TableRow key={pattern}>
            <TableCell className="font-mono text-xs">{pattern}</TableCell>
            <TableCell className="text-right font-mono tabular-nums">{count}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
