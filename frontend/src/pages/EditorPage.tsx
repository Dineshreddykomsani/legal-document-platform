import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { Download, Expand, History, Printer, Redo2, Save, Shrink, Undo2 } from "lucide-react";
import { motion } from "framer-motion";
import { legalApi } from "../lib/api";
import type { LegalDocument } from "../lib/types";
import { formatDateTime, wordCount } from "../lib/utils";
import { useDocument, useUpdateDocument } from "../features/legal/hooks";
import { AIPanel } from "../components/legal/AIPanel";
import { Button, LinkButton } from "../components/ui/Button";
import { Field, Input, Select, Textarea } from "../components/ui/Form";
import { Badge, Card, SectionHeader } from "../components/ui/Surface";
import { Skeleton } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { useToast } from "../components/system/Toast";

export default function EditorPage() {
  const id = Number(useParams().documentId);
  const documentQuery = useDocument(id);
  const updateDocument = useUpdateDocument();
  const { notify } = useToast();
  const [draft, setDraft] = useState<LegalDocument | null>(null);
  const [fullScreen, setFullScreen] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [redo, setRedo] = useState<string[]>([]);
  const lastSaved = useRef("");

  useEffect(() => {
    if (documentQuery.data) {
      setDraft(documentQuery.data);
      lastSaved.current = documentQuery.data.content;
      setHistory([documentQuery.data.content]);
    }
  }, [documentQuery.data]);

  useEffect(() => {
    if (!draft || draft.content === lastSaved.current) return;
    const timeout = window.setTimeout(() => {
      updateDocument.mutate(draft, {
        onSuccess: (saved) => {
          lastSaved.current = saved.content;
          notify({ title: "Autosaved", tone: "success" });
        },
      });
    }, 1800);
    return () => window.clearTimeout(timeout);
  }, [draft, notify, updateDocument]);

  const setContent = (content: string) => {
    setDraft((current) => (current ? { ...current, content } : current));
    setHistory((current) => [...current.slice(-24), content]);
    setRedo([]);
  };

  const undo = () => {
    if (history.length <= 1) return;
    const previous = history[history.length - 2];
    setRedo((current) => [history[history.length - 1], ...current]);
    setHistory((current) => current.slice(0, -1));
    setDraft((current) => (current ? { ...current, content: previous } : current));
  };

  const redoContent = () => {
    const next = redo[0];
    if (!next) return;
    setRedo((current) => current.slice(1));
    setHistory((current) => [...current, next]);
    setDraft((current) => (current ? { ...current, content: next } : current));
  };

  const counts = useMemo(() => ({ words: wordCount(draft?.content ?? ""), chars: draft?.content.length ?? 0 }), [draft?.content]);

  if (documentQuery.isLoading) return <Skeleton className="h-[720px]" />;
  if (!draft) return <EmptyState title="Document unavailable" description="The requested document could not be loaded." />;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={fullScreen ? "fixed inset-0 z-50 overflow-auto bg-slate-50 p-4 dark:bg-slate-950" : "grid gap-6"}>
      <SectionHeader
        eyebrow="Document editor"
        title={draft.title}
        description={`Last updated ${formatDateTime(draft.updated_at)}. Autosave keeps version history in sync with backend changes.`}
        actions={
          <>
            <Button variant="secondary" onClick={() => window.print()} icon={<Printer size={16} />}>Print</Button>
            <LinkButton href={legalApi.pdfUrl(draft.id)} icon={<Download size={16} />}>PDF</LinkButton>
          </>
        }
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_420px]">
        <Card className="overflow-hidden">
          <div className="flex flex-col gap-3 border-b border-slate-200 p-4 dark:border-slate-800 lg:flex-row lg:items-center lg:justify-between">
            <div className="grid min-w-0 flex-1 gap-3 sm:grid-cols-[1fr_170px]">
              <Field label="Title">
                <Input value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} />
              </Field>
              <Field label="Status">
                <Select value={draft.status} onChange={(event) => setDraft({ ...draft, status: event.target.value as LegalDocument["status"] })}>
                  <option value="draft">Draft</option>
                  <option value="generated">Generated</option>
                </Select>
              </Field>
            </div>
            <div className="flex flex-wrap items-end gap-2">
              <Button variant="secondary" size="icon" onClick={undo} disabled={history.length <= 1} aria-label="Undo"><Undo2 size={17} /></Button>
              <Button variant="secondary" size="icon" onClick={redoContent} disabled={!redo.length} aria-label="Redo"><Redo2 size={17} /></Button>
              <Button
                variant="secondary"
                onClick={() => updateDocument.mutate(draft, { onSuccess: () => notify({ title: "Document saved", tone: "success" }) })}
                disabled={updateDocument.isPending}
                icon={<Save size={16} />}
              >
                Save
              </Button>
              <Button variant="ghost" size="icon" onClick={() => setFullScreen((value) => !value)} aria-label="Toggle full screen">
                {fullScreen ? <Shrink size={17} /> : <Expand size={17} />}
              </Button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 bg-slate-50 px-4 py-2 dark:border-slate-800 dark:bg-slate-950">
            {["Bold", "Italic", "Clause", "Comment"].map((tool) => <Badge key={tool} tone="slate">{tool}</Badge>)}
            <span className="ml-auto text-xs font-medium text-slate-500 dark:text-slate-400">{counts.words} words • {counts.chars} characters</span>
          </div>

          <Textarea
            value={draft.content}
            onChange={(event) => setContent(event.target.value)}
            className="min-h-[620px] rounded-none border-0 bg-white p-6 font-serif text-base leading-8 shadow-none dark:bg-slate-900"
          />
        </Card>

        <div className="grid content-start gap-6">
          <AIPanel document={draft} />
          <Card className="overflow-hidden">
            <div className="flex items-center gap-2 border-b border-slate-200 px-4 py-3 dark:border-slate-800">
              <History size={17} className="text-slate-500" />
              <h2 className="font-semibold text-slate-950 dark:text-white">Version history</h2>
            </div>
            <div className="max-h-72 divide-y divide-slate-200 overflow-auto dark:divide-slate-800">
              {draft.versions.map((version) => (
                <button
                  key={version.id}
                  className="block w-full px-4 py-3 text-left transition hover:bg-slate-50 dark:hover:bg-slate-950"
                  onClick={() => setContent(version.content)}
                >
                  <span className="font-medium text-slate-950 dark:text-white">Version {version.version_number}</span>
                  <span className="block text-xs text-slate-500 dark:text-slate-400">{formatDateTime(version.created_at)}</span>
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
