import { Link } from "react-router-dom";
import { Activity, AlertTriangle, FileText, Plus, Sparkles, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";
import { useDocuments, useTemplates } from "../features/legal/hooks";
import { buttonClassName } from "../components/ui/Button";
import { Card, SectionHeader, Badge } from "../components/ui/Surface";
import { Skeleton } from "../components/ui/Skeleton";
import { formatDateTime, titleize, truncate } from "../lib/utils";

export default function DashboardPage() {
  const documents = useDocuments({ ordering: "-updated_at" });
  const templates = useTemplates();
  const items = documents.data?.results ?? [];
  const generated = items.filter((doc) => doc.status === "generated").length;
  const draft = items.filter((doc) => doc.status === "draft").length;

  const stats = [
    { label: "Active documents", value: documents.data?.count ?? 0, icon: FileText, detail: "Across document workflows" },
    { label: "Generated", value: generated, icon: Sparkles, detail: "Ready for review" },
    { label: "Drafts", value: draft, icon: Activity, detail: "Awaiting completion" },
    { label: "Templates", value: templates.data?.count ?? 0, icon: TrendingUp, detail: "Approved document types" },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid gap-6">
      <SectionHeader
        eyebrow="Overview"
        title="Dashboard"
        description="Monitor document activity, review AI insights, and launch legal document workflows from one place."
        actions={
          <>
            <Link to="/documents" className={buttonClassName({ variant: "secondary" })}>
              <FileText size={16} /> View documents
            </Link>
            <Link to="/generate" className={buttonClassName()}>
              <Plus size={16} /> New document
            </Link>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                  <Icon size={19} />
                </div>
                <Badge tone="teal">Live</Badge>
              </div>
              <p className="mt-5 text-3xl font-semibold text-slate-950 dark:text-white">{stat.value}</p>
              <p className="mt-1 text-sm font-medium text-slate-700 dark:text-slate-200">{stat.label}</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{stat.detail}</p>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <div>
              <h2 className="font-semibold text-slate-950 dark:text-white">Recent documents</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">Latest edited agreements and letters</p>
            </div>
            <Link to="/documents" className="text-sm font-medium text-teal-700 hover:text-teal-900 dark:text-teal-300">
              Open all
            </Link>
          </div>
          <div className="divide-y divide-slate-200 dark:divide-slate-800">
            {documents.isLoading ? (
              <div className="p-5"><Skeleton className="h-48" /></div>
            ) : (
              items.slice(0, 6).map((doc) => (
                <Link key={doc.id} to={`/documents/${doc.id}`} className="grid gap-2 px-5 py-4 transition hover:bg-slate-50 dark:hover:bg-slate-900 sm:grid-cols-[1fr_auto]">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-950 dark:text-white">{doc.title}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{titleize(doc.document_type)} - Updated {formatDateTime(doc.updated_at)}</p>
                  </div>
                  <Badge tone={doc.status === "generated" ? "green" : "amber"}>{doc.status}</Badge>
                </Link>
              ))
            )}
          </div>
        </Card>

        <div className="grid gap-6">
          <Card className="p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">
                <Sparkles size={19} />
              </div>
              <div>
                <h2 className="font-semibold text-slate-950 dark:text-white">AI activity</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">Gemini review tools are ready</p>
              </div>
            </div>
            <div className="mt-5 grid gap-3">
              {["Explain Clause", "Analyze Risks", "Compare Versions"].map((item) => (
                <div key={item} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-3 dark:bg-slate-950">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{item}</span>
                  <Badge tone="blue">Available</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="mt-0.5 text-amber-600" />
              <div>
                <h2 className="font-semibold text-slate-950 dark:text-white">Recent updates</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-400">
                  {items[0] ? truncate(`${items[0].title} was updated ${formatDateTime(items[0].updated_at)}.`) : "No recent document activity yet."}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
