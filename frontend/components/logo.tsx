"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

interface LogoProps {
  className?: string;
  showText?: boolean;
}

export function Logo({ className = "", showText = true }: LogoProps) {
  return (
    <Link href="/" className={`flex items-center gap-2.5 ${className}`}>
      <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-chart-4 shadow-lg shadow-primary/25">
        <Sparkles className="h-5 w-5 text-primary-foreground" />
        <div className="absolute inset-0 rounded-xl bg-gradient-to-t from-black/10 to-transparent" />
      </div>
      {showText && (
        <span className="text-xl font-bold tracking-tight">
          Tok<span className="text-gradient">Smith</span>
        </span>
      )}
    </Link>
  );
}
