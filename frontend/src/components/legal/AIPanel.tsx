import { useState } from "react";
import { Bot, Clipboard, FileWarning, RefreshCcw, Scale, Sparkles } from "lucide-react";
import type { CompareResponse, ExplainClauseResponse, LegalDocument, RiskAnalysisResponse } from "../../lib/types";
import { useAnalyzeRisks, useCompareDocuments, useExplainClause } from "../../features/legal/hooks";
import { Button } from "../ui/Button";
import { Textarea, Select, Field } from "../ui/Form";
import { Badge, Card } from "../ui/Surface";
import { Tabs } from "../ui/Tabs";
import { Skeleton } from "../ui/Skeleton";
import { useToast } from "../system/Toast";

type Mode = "explain" | "risks" | "compare";

function ResponseCard({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <Card className="p-4">
      <div className="mb-3 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">{icon}</div>
        <h3 className="font-semibold text-slate-950 dark:text-white">{title}</h3>
      </div>
      {children}
    </Card>
  );
}

function ExplainResult({ result }: { result: ExplainClauseResponse }) {
  return (
    <div className="grid gap-3">
      <ResponseCard title="Plain English" icon={<Sparkles size={17} />}>
        <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{result.plain_english_explanation}</p>
      </ResponseCard>
      <ResponseCard title="Purpose" icon={<Scale size={17} />}>
        <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{result.purpose}</p>
      </ResponseCard>
      <ResponseCard title="Business Impact" icon={<FileWarning size={17} />}>
        <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{result.business_impact}</p>
      </ResponseCard>
    </div>
  );
}

function RiskResult({ result }: { result: RiskAnalysisResponse }) {
  const tone = result.overall_risk_level === "high" ? "rose" : result.overall_risk_level === "medium" ? "amber" : "green";
  return (
    <div className="grid gap-3">
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-slate-950 dark:text-white">Risk posture</h3>
          <Badge tone={tone}>{result.overall_risk_level} risk</Badge>
        </div>
      </Card>
      {[
        ["Missing clauses", result.missing_clauses],
        ["Potential legal risks", result.potential_legal_risks],
        ["Recommendations", result.recommendations],
      ].map(([title, items]) => (
        <ResponseCard key={title as string} title={title as string} icon={<FileWarning size={17} />}>
          <ul className="grid gap-2 text-sm leading-6 text-slate-600 dark:text-slate-300">
            {(items as string[]).map((item) => <li key={item} className="rounded-md bg-slate-50 px-3 py-2 dark:bg-slate-950">{item}</li>)}
          </ul>
        </ResponseCard>
      ))}
    </div>
  );
}

function CompareResult({ result }: { result: CompareResponse }) {
  return (
    <div className="grid gap-3">
      <ResponseCard title="Executive Summary" icon={<Scale size={17} />}>
        <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{result.ai_summary.summary}</p>
      </ResponseCard>
      <ResponseCard title="Material Changes" icon={<Sparkles size={17} />}>
        <ul className="grid gap-2 text-sm text-slate-600 dark:text-slate-300">
          {result.ai_summary.material_changes.map((item) => <li key={item} className="rounded-md bg-slate-50 px-3 py-2 dark:bg-slate-950">{item}</li>)}
        </ul>
      </ResponseCard>
    </div>
  );
}

export function AIPanel({ document }: { document: LegalDocument }) {
  const [mode, setMode] = useState<Mode>("explain");
  const [clause, setClause] = useState("");
  const [base, setBase] = useState("");
  const [target, setTarget] = useState("");
  const explain = useExplainClause();
  const risks = useAnalyzeRisks();
  const compare = useCompareDocuments();
  const { notify } = useToast();

  const copyResult = async () => {
    const result = explain.data ?? risks.data ?? compare.data;
    if (!result) return;
    await navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    notify({ title: "AI response copied", tone: "success" });
  };

  const loading = explain.isPending || risks.isPending || compare.isPending;

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-slate-200 p-4 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-white dark:bg-teal-400 dark:text-slate-950">
            <Bot size={20} />
          </div>
          <div>
            <h2 className="font-semibold text-slate-950 dark:text-white">AI Assistant</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Gemini-powered legal review</p>
          </div>
        </div>
        <div className="mt-4">
          <Tabs
            value={mode}
            onChange={setMode}
            tabs={[
              { value: "explain", label: "Explain" },
              { value: "risks", label: "Risks" },
              { value: "compare", label: "Compare" },
            ]}
          />
        </div>
      </div>

      <div className="grid gap-4 p-4">
        {mode === "explain" ? (
          <>
            <Field label="Clause or paragraph">
              <Textarea value={clause} onChange={(event) => setClause(event.target.value)} placeholder="Paste the clause you want explained." />
            </Field>
            <Button disabled={!clause.trim() || loading} onClick={() => explain.mutate({ id: document.id, clause })} icon={<Sparkles size={16} />}>
              Explain Clause
            </Button>
          </>
        ) : null}

        {mode === "risks" ? (
          <Button disabled={loading} onClick={() => risks.mutate({ id: document.id })} icon={<FileWarning size={16} />}>
            Analyze Risks
          </Button>
        ) : null}

        {mode === "compare" ? (
          <>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Base version">
                <Select value={base} onChange={(event) => setBase(event.target.value)}>
                  <option value="">Select version</option>
                  {document.versions.map((version) => <option key={version.id} value={version.id}>v{version.version_number}</option>)}
                </Select>
              </Field>
              <Field label="Target version">
                <Select value={target} onChange={(event) => setTarget(event.target.value)}>
                  <option value="">Select version</option>
                  {document.versions.map((version) => <option key={version.id} value={version.id}>v{version.version_number}</option>)}
                </Select>
              </Field>
            </div>
            <Button disabled={!base || !target || loading} onClick={() => compare.mutate({ id: document.id, base: Number(base), target: Number(target) })} icon={<Scale size={16} />}>
              Compare Versions
            </Button>
          </>
        ) : null}

        {loading ? <Skeleton className="h-40" /> : null}

        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" disabled={!explain.data && !risks.data && !compare.data} onClick={copyResult} icon={<Clipboard size={15} />}>
            Copy
          </Button>
          <Button variant="secondary" size="sm" disabled={loading} onClick={() => mode === "risks" && risks.mutate({ id: document.id })} icon={<RefreshCcw size={15} />}>
            Regenerate
          </Button>
        </div>

        {explain.data && mode === "explain" ? <ExplainResult result={explain.data} /> : null}
        {risks.data && mode === "risks" ? <RiskResult result={risks.data} /> : null}
        {compare.data && mode === "compare" ? <CompareResult result={compare.data} /> : null}
      </div>
    </Card>
  );
}
