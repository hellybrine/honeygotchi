import { Badge, actionVariant } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { fetchUpstream } from '@/lib/api';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

type Policy = Record<string, Record<string, number>>;

async function loadPolicy(): Promise<Policy> {
  try {
    return await fetchUpstream<Policy>('/api/policy');
  } catch {
    return {};
  }
}

export default async function PolicyPage() {
  const policy = await loadPolicy();
  const states = Object.keys(policy).sort();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Learned policy</CardTitle>
      </CardHeader>
      <CardContent>
        {states.length === 0 ? (
          <div className="py-12 text-center text-sm text-muted-foreground">
            Agent hasn&apos;t learned anything yet. Send some traffic to the honeypot.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>State (pattern · phase)</TableHead>
                <TableHead>Best action</TableHead>
                <TableHead>Q-values</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {states.map((state) => {
                const values = policy[state];
                const best = Object.entries(values).reduce((a, b) => (b[1] > a[1] ? b : a));
                return (
                  <TableRow key={state}>
                    <TableCell className="font-mono text-xs">{state.replace('|', ' · ')}</TableCell>
                    <TableCell>
                      <Badge variant={actionVariant(best[0])}>{best[0]}</Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(values).map(([action, q]) => (
                          <span key={action} className="tabular-nums text-muted-foreground">
                            {action}: <span className={q === best[1] ? 'text-foreground' : ''}>{q.toFixed(2)}</span>
                          </span>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
