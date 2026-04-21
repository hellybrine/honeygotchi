import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { fetchUpstream, type Session } from '@/lib/api';
import { formatDuration, formatRelativeTime } from '@/lib/utils';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function loadSessions(): Promise<Session[]> {
  try {
    return await fetchUpstream<Session[]>('/api/sessions?limit=100');
  } catch {
    return [];
  }
}

export default async function SessionsPage() {
  const sessions = await loadSessions();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent sessions</CardTitle>
      </CardHeader>
      <CardContent>
        {sessions.length === 0 ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            No sessions recorded yet. Try <code>ssh user@localhost -p 2222</code>.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Status</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>IP</TableHead>
                <TableHead>User</TableHead>
                <TableHead className="text-right">Commands</TableHead>
                <TableHead className="text-right">Duration</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sessions.map((s) => (
                <TableRow key={s.session_id}>
                  <TableCell>
                    {s.ended_at == null ? (
                      <Badge variant="success">active</Badge>
                    ) : (
                      <Badge variant="secondary">ended</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatRelativeTime(s.started_at)}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{s.client_ip}</TableCell>
                  <TableCell className="font-mono text-xs">{s.username}</TableCell>
                  <TableCell className="text-right font-mono tabular-nums">
                    {s.command_count}
                  </TableCell>
                  <TableCell className="text-right font-mono tabular-nums">
                    {formatDuration(s.duration)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
