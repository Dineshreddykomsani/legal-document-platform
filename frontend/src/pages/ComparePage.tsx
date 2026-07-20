import { useMemo, useState } from "react";
import { Download, FileDiff, Scale } from "lucide-react";
import { motion } from "framer-motion";
import { useCompareDocuments, useDocument, useDocuments } from "../features/legal/hooks";
import { Button } from "../components/ui/Button";
import { Field, Select } from "../components/ui/Form";
import { Badge, Card, SectionHeader } from "../components/ui/Surface";
import { EmptyState } from "../components/ui/EmptyState";
import { ComparisonSummary, SplitVersionView } from "../components/legal/ComparePanel";
import { titleize } from "../lib/utils";

export default function ComparePage() {
  const documents = useDocuments({ ordering: "-updated_at" });
  const [documentId, setDocumentId] = useState("");
  const [baseId, setBaseId] = useState("");
  const [targetId, setTargetId] = useState("");
  const detail = useDocument(documentId ? Number(documentId) : undefined);
  const compare = useCompareDocuments();

  const selected = detail.data;
  const base = useMemo(() => selected?.versions.find((version) => version.id === Number(baseId)), [selected, baseId]);
  const target = useMemo(() => selected?.versions.find((version) => version.id === Number(targetId)), [selected, targetId]);

  const exportComparison = () => {
    if (!compare.data) return;
    const blob = new Blob([JSON.stringify(compare.data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "comparison.json";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid gap-6">
      <SectionHeader
        eyebrow="Version intelligence"
        title="Compare Documents"
        description="Review side-by-side versions, highlighted modifications, and Gemini-generated executive summaries."
        actions={<Button variant="secondary" disabled={!compare.data} onClick={exportComparison} icon={<Download size={16} />}>Export comparison</Button>}
      />

      <Card className="p-4">
        <div className="grid gap-3 lg:grid-cols-[1fr_180px_180px_auto]">
          <Field label="Document">
            <Select value={documentId} onChange={(event) => { setDocumentId(event.target.value); setBaseId(""); setTargetId(""); }}>
              <option value="">Select document</option>
              {documents.data?.results.map((doc) => <option key={doc.id} value={doc.id}>{doc.title} · {titleize(doc.document_type)}</option>)}
            </Select>
          </Field>
          <Field label="Base version">
            <Select value={baseId} onChange={(event) => setBaseId(event.target.value)} disabled={!selected}>
              <option value="">Base</option>
              {selected?.versions.map((version) => <option key={version.id} value={version.id}>v{version.version_number}</option>)}
            </Select>
          </Field>
          <Field label="Target version">
            <Select value={targetId} onChange={(event) => setTargetId(event.target.value)} disabled={!selected}>
              <option value="">Target</option>
              {selected?.versions.map((version) => <option key={version.id} value={version.id}>v{version.version_number}</option>)}
            </Select>
          </Field>
          <div className="flex items-end">
            <Button disabled={!selected || !baseId || !targetId || compare.isPending} onClick={() => compare.mutate({ id: Number(documentId), base: Number(baseId), target: Number(targetId) })} icon={<Scale size={16} />}>
              Compare
            </Button>
          </div>
        </div>
      </Card>

      {!selected ? (
        <EmptyState title="Select a document" description="Choose a document with version history to begin a professional comparison review." />
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="blue">{selected.versions.length} versions</Badge>
            <Badge tone={selected.status === "generated" ? "green" : "amber"}>{selected.status}</Badge>
          </div>
          <SplitVersionView base={base} target={target} />
          {compare.data ? <ComparisonSummary result={compare.data} /> : (
            <Card className="grid min-h-48 place-items-center p-6 text-center">
              <div>
                <FileDiff className="mx-auto text-slate-400" size={32} />
                <p className="mt-3 text-sm font-medium text-slate-600 dark:text-slate-300">Run a comparison to see highlighted additions, removals, and AI summary.</p>
              </div>
            </Card>
          )}
        </>
      )}
    </motion.div>
  );
}
