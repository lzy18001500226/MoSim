import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Imagine Worlds - Build Your Dreams in 3D",
  description:
    "A creative learning platform where children build amazing 3D worlds with an AI companion.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
