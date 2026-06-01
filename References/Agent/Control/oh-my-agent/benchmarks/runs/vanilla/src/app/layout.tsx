import type { Metadata } from 'next';
import { Nunito } from 'next/font/google';
import './globals.css';

const nunito = Nunito({
  variable: '--font-nunito',
  subsets: ['latin'],
  weight: ['400', '600', '700', '800', '900'],
});

export const metadata: Metadata = {
  title: 'DreamWorld - Build Your Imagination',
  description: 'A magical 3D creative learning platform for young builders and dreamers',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${nunito.variable} h-full`}>
      <body className="min-h-full antialiased" style={{ fontFamily: 'Nunito, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}
