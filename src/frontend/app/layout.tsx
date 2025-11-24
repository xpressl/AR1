'use client';

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../app/globals.css';
import '../styles/alerts.css';
import '../styles/components.css';
import { Providers } from './providers';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

// Note: metadata export doesn't work in 'use client' components
// Move to a separate layout.metadata.ts or use generateMetadata in page.tsx

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="AR Control Hub - Accounts Receivable Management System" />
        <title>AR Control Hub</title>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="min-h-screen bg-neutral-50 text-neutral-900 antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
