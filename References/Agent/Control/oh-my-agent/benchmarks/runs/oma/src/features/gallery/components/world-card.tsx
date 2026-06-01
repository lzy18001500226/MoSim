"use client";

import Link from "next/link";

interface WorldCardProps {
  id: string;
  title: string;
  createdAt: string;
  isSample?: boolean;
}

export function WorldCard({ id, title, createdAt, isSample }: WorldCardProps) {
  return (
    <Link
      href={`/explore/${id}`}
      className="block bg-[var(--color-surface)] rounded-2xl border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group"
    >
      <div className="h-36 bg-gradient-to-br from-[var(--color-primary)]/20 to-[var(--color-accent)]/20 flex items-center justify-center">
        <span className="text-4xl group-hover:scale-110 transition-transform">🌍</span>
      </div>
      <div className="p-4">
        <h3 className="font-bold text-sm truncate">{title}</h3>
        <div className="flex items-center justify-between mt-1">
          <p className="text-xs text-[var(--color-text-muted)]">
            {new Date(createdAt).toLocaleDateString()}
          </p>
          {isSample && (
            <span className="text-xs px-2 py-0.5 bg-[var(--color-warning)]/30 rounded-full">
              Sample
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
