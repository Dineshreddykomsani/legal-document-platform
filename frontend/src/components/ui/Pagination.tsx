import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./Button";

export function Pagination({ page, count, pageSize, onPageChange }: { page: number; count: number; pageSize: number; onPageChange: (page: number) => void }) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  return (
    <div className="flex flex-col gap-3 border-t border-slate-200 px-4 py-3 text-sm text-slate-600 dark:border-slate-800 dark:text-slate-400 sm:flex-row sm:items-center sm:justify-between">
      <span>
        Page <strong className="text-slate-950 dark:text-white">{page}</strong> of {totalPages}
      </span>
      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)} icon={<ChevronLeft size={15} />}>
          Previous
        </Button>
        <Button variant="secondary" size="sm" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
          Next <ChevronRight size={15} />
        </Button>
      </div>
    </div>
  );
}
