import { useMemo, useState } from "react";
import { MoreHorizontal, Trash2, Eye, ArrowUpDown } from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { LegalDocumentListItem } from "../../lib/types";
import { formatDate, titleize } from "../../lib/utils";
import { Badge, Card } from "../ui/Surface";
import { Button } from "../ui/Button";
import { EmptyState } from "../ui/EmptyState";
import { Pagination } from "../ui/Pagination";
import { TableSkeleton } from "../ui/Skeleton";

export function StatusBadge({ status }: { status: LegalDocumentListItem["status"] }) {
  return <Badge tone={status === "generated" ? "green" : "amber"}>{status}</Badge>;
}

export function DocumentTable({
  documents,
  count,
  page,
  loading,
  onPageChange,
  onDelete,
  onSort,
}: {
  documents: LegalDocumentListItem[];
  count: number;
  page: number;
  loading: boolean;
  onPageChange: (page: number) => void;
  onDelete: (id: number) => void;
  onSort: (field: string) => void;
}) {
  const [selected, setSelected] = useState<number[]>([]);
  const navigate = useNavigate();
  const allSelected = documents.length > 0 && documents.every((doc) => selected.includes(doc.id));

  const selectedLabel = useMemo(() => (selected.length ? `${selected.length} selected` : "Bulk actions"), [selected.length]);

  if (loading) {
    return (
      <Card className="p-4">
        <TableSkeleton rows={8} />
      </Card>
    );
  }

  if (!documents.length) {
    return <EmptyState title="No documents found" description="Generate a document or adjust your filters to find active work." />;
  }

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">{selectedLabel}</span>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" disabled={!selected.length} icon={<Trash2 size={15} />}>
            Archive
          </Button>
          <Button variant="secondary" size="sm" disabled={!selected.length}>
            Export
          </Button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[880px] border-collapse text-left">
          <thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:bg-slate-950 dark:text-slate-400">
            <tr>
              <th className="w-12 px-4 py-3">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={(event) => setSelected(event.target.checked ? documents.map((doc) => doc.id) : [])}
                  aria-label="Select all documents"
                />
              </th>
              <th className="px-4 py-3">
                <button className="inline-flex items-center gap-1" onClick={() => onSort("title")}>
                  Document <ArrowUpDown size={13} />
                </button>
              </th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">
                <button className="inline-flex items-center gap-1" onClick={() => onSort("-updated_at")}>
                  Updated <ArrowUpDown size={13} />
                </button>
              </th>
              <th className="px-4 py-3">Versions</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 text-sm dark:divide-slate-800">
            {documents.map((doc) => (
              <tr key={doc.id} className="transition hover:bg-slate-50 dark:hover:bg-slate-900/70">
                <td className="px-4 py-4">
                  <input
                    type="checkbox"
                    checked={selected.includes(doc.id)}
                    onChange={(event) =>
                      setSelected((current) => (event.target.checked ? [...current, doc.id] : current.filter((id) => id !== doc.id)))
                    }
                    aria-label={`Select ${doc.title}`}
                  />
                </td>
                <td className="px-4 py-4">
                  <button onClick={() => navigate(`/documents/${doc.id}`)} className="text-left">
                    <span className="block font-semibold text-slate-950 dark:text-white">{doc.title}</span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">Created {formatDate(doc.created_at)}</span>
                  </button>
                </td>
                <td className="px-4 py-4 text-slate-600 dark:text-slate-300">{titleize(doc.document_type)}</td>
                <td className="px-4 py-4"><StatusBadge status={doc.status} /></td>
                <td className="px-4 py-4 text-slate-600 dark:text-slate-300">{formatDate(doc.updated_at)}</td>
                <td className="px-4 py-4 text-slate-600 dark:text-slate-300">{doc.version_count}</td>
                <td className="px-4 py-4">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="icon" onClick={() => navigate(`/documents/${doc.id}`)} aria-label="Open document">
                      <Eye size={17} />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => onDelete(doc.id)} aria-label="Delete document">
                      <Trash2 size={17} />
                    </Button>
                    <Button variant="ghost" size="icon" aria-label="More actions">
                      <MoreHorizontal size={17} />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={page} count={count} pageSize={10} onPageChange={onPageChange} />
    </Card>
  );
}
