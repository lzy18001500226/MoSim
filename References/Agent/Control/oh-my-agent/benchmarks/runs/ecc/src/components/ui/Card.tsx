"use client";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export function Card({ children, className = "", onClick, hoverable = false }: CardProps) {
  const base = "bg-white rounded-2xl shadow-md border border-sky/10 overflow-hidden";
  const hover = hoverable ? "transition-all duration-200 hover:-translate-y-1 hover:shadow-xl cursor-pointer" : "";

  return (
    <div onClick={onClick} className={`${base} ${hover} ${className}`}>
      {children}
    </div>
  );
}
