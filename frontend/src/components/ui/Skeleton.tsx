import { cn } from "../../lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("relative overflow-hidden rounded-md bg-slate-200 dark:bg-slate-800", className, "after:absolute after:inset-0 after:-translate-x-full after:bg-gradient-to-r after:from-transparent after:via-white/45 after:to-transparent after:animate-[shimmer_1.6s_infinite] dark:after:via-white/10")} />;
}

export function TableSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="grid gap-2">
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} className="h-12" />
      ))}
    </div>
  );
}
