import type { Metadata } from 'next';
import Link from 'next/link';
import { Activity } from 'lucide-react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Honeygotchi',
  description: 'Adaptive SSH honeypot dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <header className="border-b">
          <div className="container flex h-14 items-center justify-between">
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <Activity className="h-4 w-4" />
              Honeygotchi
            </Link>
            <nav className="flex items-center gap-4 text-sm">
              <Link href="/" className="text-muted-foreground hover:text-foreground">
                Overview
              </Link>
              <Link href="/sessions" className="text-muted-foreground hover:text-foreground">
                Sessions
              </Link>
              <Link href="/policy" className="text-muted-foreground hover:text-foreground">
                Policy
              </Link>
            </nav>
          </div>
        </header>
        <main className="container py-8">{children}</main>
      </body>
    </html>
  );
}
