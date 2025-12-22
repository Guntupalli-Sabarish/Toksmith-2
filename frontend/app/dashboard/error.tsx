"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle, RefreshCw, LayoutDashboard } from "lucide-react";
import Link from "next/link";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Dashboard error:", error);
  }, [error]);

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="max-w-md w-full text-center">
        {/* Icon */}
        <div className="mx-auto h-14 w-14 rounded-xl bg-destructive/10 flex items-center justify-center mb-6">
          <AlertTriangle className="h-7 w-7 text-destructive" />
        </div>

        {/* Message */}
        <h2 className="text-xl font-bold mb-2">Dashboard Error</h2>
        <p className="text-muted-foreground mb-6">
          We couldn&apos;t load this section. This might be a temporary issue.
        </p>

        {/* Error details (dev only) */}
        {process.env.NODE_ENV === "development" && (
          <div className="mb-6 p-4 rounded-lg bg-muted text-left overflow-auto">
            <p className="text-sm font-mono text-destructive break-all">
              {error.message}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Button onClick={reset} variant="default" size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Retry
          </Button>
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-2">
              <LayoutDashboard className="h-4 w-4" />
              Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
