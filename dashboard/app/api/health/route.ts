export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  return Response.json({ status: 'healthy', timestamp: new Date().toISOString() });
}
