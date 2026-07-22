import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Building2, Check, ChevronLeft, ChevronRight, FileText, ImageUp, Save, WandSparkles } from "lucide-react";
import { motion } from "framer-motion";
import { useGenerateDocument, useTemplates } from "../features/legal/hooks";
import { Button } from "../components/ui/Button";
import { Field, Input } from "../components/ui/Form";
import { Badge, Card, SectionHeader } from "../components/ui/Surface";
import { Skeleton } from "../components/ui/Skeleton";
import { titleize } from "../lib/utils";
import { useToast } from "../components/system/Toast";
import type { CompanyBranding, DocumentTemplate } from "../lib/types";
import { API_BASE_URL } from "../lib/api";

const steps = ["Document", "Template", "Details", "Branding", "Preview", "Generate"];
const schema = z.object({ title: z.string().min(2, "A document title is required") });

const brandingFields: Array<{ name: keyof CompanyBranding; label: string }> = [
  { name: "company_name", label: "Company name" },
  { name: "address", label: "Address" },
  { name: "phone", label: "Phone number" },
  { name: "email", label: "Email" },
  { name: "website", label: "Website" },
  { name: "registration_number", label: "Registration number" },
  { name: "gst_number", label: "GST number" },
];

function TemplateThumb({ template }: { template: DocumentTemplate }) {
  const primary = template.color_scheme?.primary ?? "#0f172a";
  const accent = template.color_scheme?.accent ?? "#0f766e";
  return (
    <div className="h-44 rounded-md border border-slate-200 bg-white p-4 shadow-inner dark:border-slate-700">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="h-2 w-24 rounded-sm" style={{ background: primary }} />
          <div className="mt-2 h-1.5 w-32 rounded-sm bg-slate-200" />
          <div className="mt-1.5 h-1.5 w-20 rounded-sm bg-slate-200" />
        </div>
        <div className="grid h-10 w-10 place-items-center rounded-sm border text-[10px] font-semibold" style={{ borderColor: accent, color: accent }}>
          LOGO
        </div>
      </div>
      <div className="mt-5 space-y-2">
        <div className="h-2.5 w-36 rounded-sm" style={{ background: accent }} />
        <div className="h-1.5 w-full rounded-sm bg-slate-200" />
        <div className="h-1.5 w-11/12 rounded-sm bg-slate-200" />
        <div className="h-1.5 w-10/12 rounded-sm bg-slate-200" />
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="h-8 rounded-sm border border-slate-200" />
        <div className="h-8 rounded-sm border border-slate-200" />
      </div>
      <div className="mt-4 h-px" style={{ background: accent }} />
    </div>
  );
}

export default function GeneratorPage() {
  const [step, setStep] = useState(0);
  const [documentType, setDocumentType] = useState("");
  const [templateId, setTemplateId] = useState<number | undefined>();
  const [fields, setFields] = useState<Record<string, string>>({});
  const [branding, setBranding] = useState<CompanyBranding>({});
  const [logo, setLogo] = useState<File | null>(null);
  const [generationError, setGenerationError] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");
  const templates = useTemplates();
  const generate = useGenerateDocument();
  const navigate = useNavigate();
  const { notify } = useToast();
  const form = useForm<{ title: string }>({ resolver: zodResolver(schema), defaultValues: { title: "" } });
  const title = form.watch("title");

  const grouped = useMemo(() => {
    const map = new Map<string, DocumentTemplate[]>();
    for (const item of templates.data?.results ?? []) {
      const bucket = map.get(item.document_type) ?? [];
      bucket.push(item);
      map.set(item.document_type, bucket);
    }
    return Array.from(map.entries()).map(([type, items]) => ({ type, items }));
  }, [templates.data]);

  const variants = grouped.find((group) => group.type === documentType)?.items ?? [];
  const template = variants.find((item) => item.id === templateId) ?? variants[0];
  const missing = template?.required_fields.filter((field) => !fields[field.name]?.trim()) ?? [];

  const canContinue =
    step === 0 ? Boolean(documentType) : step === 1 ? Boolean(template) : step === 2 ? title.trim() && !missing.length : true;

  const preview = template
    ? [
        title || template.name,
        "",
        `Template: ${template.theme || template.name}`,
        branding.company_name ? `Company: ${branding.company_name}` : "Company: Text-based professional header will be generated",
        "",
        ...template.required_fields.map((field) => `${field.label}: ${fields[field.name] ?? ""}`),
      ].join("\n")
    : "";

  const runGenerate = async () => {
    if (!template) {
      setGenerationError("Select a document template before generating.");
      return;
    }
    const ok = await form.trigger();
    if (!ok || missing.length) {
      setGenerationError(`Complete all required fields before generating${missing.length ? `: ${missing.map((field) => field.label).join(", ")}` : "."}`);
      return;
    }
    setGenerationError("");
    generate.mutate(
      {
        document_type: template.document_type,
        template_id: template.id,
        title: form.getValues("title") || template.name,
        fields,
        branding,
        company_logo: logo,
        save: true,
      },
      {
        onSuccess: (data) => {
          notify({ title: "Document generated", tone: "success" });
          const url = data.pdf_url ?? (data.document ? `/api/legal/documents/${data.document.id}/download-pdf/` : "");
          setPdfUrl(url && url.startsWith("http") ? url : `${API_BASE_URL}${url}`);
          if (data.document) window.setTimeout(() => navigate(`/documents/${data.document!.id}`), 1200);
        },
        onError: (error) => {
          const message = error instanceof Error ? error.message : "Document generation failed.";
          setGenerationError(message);
          notify({ title: message, tone: "error" });
        },
      },
    );
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid gap-6">
      <SectionHeader eyebrow="Document automation" title="Professional Document Generator" description="Choose a document, select a production template, add business details, preview, and generate a branded PDF." />

      <Card className="p-4">
        <div className="grid gap-3 md:grid-cols-6">
          {steps.map((label, index) => (
            <div key={label} className="flex items-center gap-3 rounded-md bg-slate-50 p-3 dark:bg-slate-950">
              <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${index <= step ? "bg-teal-700 text-white dark:bg-teal-400 dark:text-slate-950" : "bg-slate-200 text-slate-600 dark:bg-slate-800 dark:text-slate-300"}`}>
                {index < step ? <Check size={16} /> : index + 1}
              </div>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{label}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="min-h-[560px] p-6">
        {templates.isLoading ? <Skeleton className="h-96" /> : null}

        {step === 0 && (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {grouped.map((group) => (
              <button
                key={group.type}
                onClick={() => {
                  setDocumentType(group.type);
                  setTemplateId(group.items[0]?.id);
                }}
                className={`rounded-lg border p-5 text-left transition ${documentType === group.type ? "border-teal-600 bg-teal-50 dark:border-teal-400 dark:bg-teal-950" : "border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700"}`}
              >
                <FileText className="mb-4 text-teal-700 dark:text-teal-300" size={24} />
                <h3 className="font-semibold text-slate-950 dark:text-white">{titleize(group.type)}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{group.items.length} professional templates with shared legal content.</p>
                <Badge tone="slate">{group.items[0]?.required_fields.length ?? 0} fields</Badge>
              </button>
            ))}
          </div>
        )}

        {step === 1 && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {variants.map((item) => (
              <button
                key={item.id}
                onClick={() => setTemplateId(item.id)}
                className={`rounded-lg border p-4 text-left transition ${template?.id === item.id ? "border-teal-600 bg-teal-50 dark:border-teal-400 dark:bg-teal-950" : "border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700"}`}
              >
                <TemplateThumb template={item} />
                <h3 className="mt-4 font-semibold text-slate-950 dark:text-white">{item.theme || item.name}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{item.description}</p>
              </button>
            ))}
          </div>
        )}

        {step === 2 && template && (
          <div className="mx-auto grid max-w-4xl gap-5">
            <Field label="Document title" error={form.formState.errors.title?.message}>
              <Input {...form.register("title")} placeholder={template.name} />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              {template.required_fields.map((field) => (
                <Field key={field.name} label={field.label}>
                  <Input value={fields[field.name] ?? ""} onChange={(event) => setFields({ ...fields, [field.name]: event.target.value })} />
                </Field>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="mx-auto grid max-w-4xl gap-5">
            <div className="flex items-center gap-3">
              <Building2 className="text-teal-700 dark:text-teal-300" size={24} />
              <div>
                <h2 className="font-semibold text-slate-950 dark:text-white">Company branding</h2>
                <p className="text-sm text-slate-600 dark:text-slate-400">All fields are optional. A text letterhead is generated when no logo is uploaded.</p>
              </div>
            </div>
            <Field label="Company logo">
              <div className="flex flex-wrap items-center gap-3">
                <Input type="file" accept="image/png,image/jpeg,image/jpg" onChange={(event) => setLogo(event.target.files?.[0] ?? null)} />
                <Badge tone={logo ? "green" : "slate"}>{logo ? logo.name : "No logo selected"}</Badge>
              </div>
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              {brandingFields.map((field) => (
                <Field key={field.name} label={field.label}>
                  <Input value={branding[field.name] ?? ""} onChange={(event) => setBranding({ ...branding, [field.name]: event.target.value })} />
                </Field>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="mx-auto max-w-4xl">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Preview</h2>
              <Badge tone="blue">{template?.theme}</Badge>
            </div>
            <pre className="min-h-96 whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm leading-7 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">{preview}</pre>
          </div>
        )}

        {step === 5 && (
          <div className="grid min-h-96 place-items-center text-center">
            <div>
              {generate.isSuccess ? <Save className="mx-auto text-emerald-600" size={42} /> : <WandSparkles className="mx-auto text-teal-700 dark:text-teal-300" size={42} />}
              <h2 className="mt-4 text-xl font-semibold text-slate-950 dark:text-white">{generate.isSuccess ? "Document saved" : "Ready to generate PDF"}</h2>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{generate.isSuccess ? "Opening the editor now." : "The selected layout, clauses, branding, and logo will be saved with the document."}</p>
              {!generate.isSuccess ? (
                <>
                  <Button className="mt-5" disabled={generate.isPending} onClick={runGenerate} icon={logo ? <ImageUp size={16} /> : <WandSparkles size={16} />}>
                    {generate.isPending ? "Generating document..." : "Generate document"}
                  </Button>
                  {generationError ? (
                    <p className="mx-auto mt-4 max-w-xl rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
                      {generationError}
                    </p>
                  ) : null}
                </>
              ) : pdfUrl ? (
                <a className="mt-5 inline-flex h-10 items-center justify-center rounded-md bg-teal-700 px-4 text-sm font-medium text-white hover:bg-teal-800" href={pdfUrl} target="_blank" rel="noreferrer">
                  Open PDF
                </a>
              ) : null}
            </div>
          </div>
        )}
      </Card>

      <div className="flex justify-between">
        <Button variant="secondary" disabled={step === 0 || generate.isPending} onClick={() => setStep((value) => Math.max(0, value - 1))} icon={<ChevronLeft size={16} />}>
          Back
        </Button>
        {step < 5 ? (
          <Button
            disabled={!canContinue}
            onClick={async () => {
              if (step === 2) {
                const ok = await form.trigger();
                if (!ok || missing.length) return;
              }
              setStep((value) => value + 1);
            }}
          >
            Continue <ChevronRight size={16} />
          </Button>
        ) : null}
      </div>
    </motion.div>
  );
}
