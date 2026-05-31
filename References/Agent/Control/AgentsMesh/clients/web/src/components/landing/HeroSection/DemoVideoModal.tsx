"use client";

import { useEffect } from "react";

interface DemoVideoModalProps {
  open: boolean;
  onClose: () => void;
  iframeTitle: string;
}

export function DemoVideoModal({ open, onClose, iframeTitle }: DemoVideoModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8 bg-[var(--azure-bg-deeper)]/85 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={iframeTitle}
    >
      <button
        onClick={onClose}
        aria-label="Close"
        className="absolute top-6 right-6 w-10 h-10 rounded-full azure-glass border border-white/10 text-foreground hover:text-[var(--azure-cyan)] hover:border-[var(--azure-cyan)]/40 transition-all flex items-center justify-center"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div
        className="w-full max-w-5xl azure-glass rounded-3xl border border-white/10 azure-glow-cyan-lg p-3 sm:p-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative rounded-2xl overflow-hidden bg-[var(--azure-bg-deeper)]" style={{ aspectRatio: "16/9" }}>
          <iframe
            src="https://www.youtube-nocookie.com/embed/FZrUO0tim0U?autoplay=1&rel=0&modestbranding=1"
            title={iframeTitle}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
            className="absolute inset-0 w-full h-full"
          />
        </div>
      </div>
    </div>
  );
}
