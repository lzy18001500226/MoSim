export function Divider({ text }: { text: string }) {
  return (
    <div className="relative my-2">
      <div className="absolute inset-0 flex items-center">
        <div className="w-full border-t border-white/10" />
      </div>
      <div className="relative flex justify-center">
        <span className="bg-[var(--azure-bg-card)] px-3 text-[10px] font-headline tracking-[0.2em] uppercase text-[var(--azure-text-muted)]">
          {text}
        </span>
      </div>
    </div>
  );
}
