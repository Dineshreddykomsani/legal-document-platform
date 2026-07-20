import type { ReactNode } from "react";
import { FileSearch } from "lucide-react";
import { Card } from "./Surface";

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <Card className="flex min-h-64 flex-col items-center justify-center px-6 py-12 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300">
        <FileSearch size={22} />
      </div>
      <h3 className="text-base font-semibold text-slate-950 dark:text-white">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600 dark:text-slate-400">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </Card>
  );
}
