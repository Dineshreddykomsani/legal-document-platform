import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export function Tabs<T extends string>({ value, onChange, tabs }: { value: T; onChange: (value: T) => void; tabs: { value: T; label: string; icon?: ReactNode }[] }) {
  return (
    <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1 dark:border-slate-800 dark:bg-slate-950">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          type="button"
          onClick={() => onChange(tab.value)}
          className={cn(
            "inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-medium transition",
            value === tab.value
              ? "bg-white text-slate-950 shadow-sm dark:bg-slate-800 dark:text-white"
              : "text-slate-600 hover:text-slate-950 dark:text-slate-400 dark:hover:text-white",
          )}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
