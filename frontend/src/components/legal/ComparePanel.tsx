import type { CompareResponse, DocumentVersion } from "../../lib/types";
import { Card, Badge } from "../ui/Surface";

export function DiffLine({ line }: { line: string }) {
  const added = line.startsWith("+") && !line.startsWith("+++");
  const removed = line.startsWith("-") && !line.startsWith("---");
  const meta = line.startsWith("@@") || line.startsWith("+++") || line.startsWith("---");
  return (
    <div
      className={
        added
          ? "bg-emerald-50 px-3 py-1 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200"
          : removed
            ? "bg-rose-50 px-3 py-1 text-rose-800 dark:bg-rose-950 dark:text-rose-200"
            : meta
              ? "bg-slate-100 px-3 py-1 text-slate-500 dark:bg-slate-800 dark:text-slate-400"
              : "px-3 py-1 text-slate-600 dark:text-slate-300"
      }
    >
      {line || " "}
    </div>
  );
}

export function SplitVersionView({ base, target }: { base?: DocumentVersion; target?: DocumentVersion }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {[["Base", base], ["Target", target]].map(([label, version]) => (
        <Card key={label as string} className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
            <h3 className="font-semibold text-slate-950 dark:text-white">{label as string}</h3>
            {version ? <Badge tone="blue">v{(version as DocumentVersion).version_number}</Badge> : null}
          </div>
          <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap p-4 text-sm leading-6 text-slate-700 dark:text-slate-300">
            {version ? (version as DocumentVersion).content : "Select a version"}
          </pre>
        </Card>
      ))}
    </div>
  );
}

export function ComparisonSummary({ result }: { result: CompareResponse }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
      <Card className="p-5">
        <h3 className="font-semibold text-slate-950 dark:text-white">Executive summary</h3>
        <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{result.ai_summary.summary}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge tone="green">{result.added_content.length} additions</Badge>
          <Badge tone="rose">{result.removed_content.length} removals</Badge>
        </div>
      </Card>
      <Card className="overflow-hidden">
        <div className="border-b border-slate-200 px-4 py-3 dark:border-slate-800">
          <h3 className="font-semibold text-slate-950 dark:text-white">Unified changes</h3>
        </div>
        <div className="max-h-[420px] overflow-auto font-mono text-xs leading-5">
          {result.modified_content.map((line, index) => <DiffLine key={`${line}-${index}`} line={line} />)}
        </div>
      </Card>
    </div>
  );
}
