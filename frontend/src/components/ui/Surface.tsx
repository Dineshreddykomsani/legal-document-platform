import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section className={cn("rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900", className)}>
      {children}
    </section>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0">
        {eyebrow ? <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-teal-700 dark:text-teal-300">{eyebrow}</p> : null}
        <h1 className="text-2xl font-semibold tracking-normal text-slate-950 dark:text-white">{title}</h1>
        {description ? <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-400">{description}</p> : null}
      </div>
      {actions ? <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

export function Badge({ children, tone = "slate" }: { children: ReactNode; tone?: "slate" | "green" | "amber" | "rose" | "blue" | "teal" }) {
  const tones = {
    slate: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200",
    green: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
    amber: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
    rose: "bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
    blue: "bg-sky-50 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
    teal: "bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300",
  };
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold capitalize", tones[tone])}>{children}</span>;
}

export function Chip({ children, active }: { children: ReactNode; active?: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium",
        active
          ? "border-teal-600 bg-teal-50 text-teal-800 dark:border-teal-400 dark:bg-teal-950 dark:text-teal-200"
          : "border-slate-200 bg-white text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300",
      )}
    >
      {children}
    </span>
  );
}
