import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export function Tooltip({ label, children, align = "center" }: { label: string; children: ReactNode; align?: "start" | "center" | "end" }) {
  const alignment = {
    start: "left-0",
    center: "left-1/2 -translate-x-1/2",
    end: "right-0",
  };

  return (
    <span className="group relative inline-flex">
      {children}
      <span className={cn("pointer-events-none absolute top-full z-20 mt-2 whitespace-nowrap rounded-md bg-slate-950 px-2 py-1 text-xs font-medium text-white opacity-0 shadow-lg transition group-hover:opacity-100 dark:bg-white dark:text-slate-950", alignment[align])}>
        {label}
      </span>
    </span>
  );
}
