import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, ChevronLeft, ChevronRight, FileText, Save, WandSparkles } from "lucide-react";
import { motion } from "framer-motion";
import { useGenerateDocument, useTemplates } from "../features/legal/hooks";
import { Button } from "../components/ui/Button";
import { Field, Input } from "../components/ui/Form";
import { Badge, Card, SectionHeader } from "../components/ui/Surface";
import { Skeleton } from "../components/ui/Skeleton";
import { titleize } from "../lib/utils";
import { useToast } from "../components/system/Toast";

const steps = ["Template", "Details", "Preview", "Generate", "Save"];
const schema = z.object({ title: z.string().min(2, "A document title is required") });

export default function GeneratorPage() {
  const [step, setStep] = useState(0);
  const [templateType, setTemplateType] = useState("");
  const [fields, setFields] = useState<Record<string, string>>({});
  const templates = useTemplates();
  const generate = useGenerateDocument();
  const navigate = useNavigate();
  const { notify } = useToast();
  const template = useMemo(() => templates.data?.results.find((item) => item.document_type === templateType) ?? templates.data?.results[0], [templates.data, templateType]);
  const form = useForm<{ title: string }>({ resolver: zodResolver(schema), defaultValues: { title: "" } });
  const title = form.watch("title");

  const missing = template?.required_fields.filter((field) => !fields[field.name]?.trim()) ?? [];
  const canContinue = step === 0 ? Boolean(template) : step === 1 ? title.trim() && !missing.length : true;
  const preview = template ? template.required_fields.reduce((text, field) => `${text}${field.label}: ${fields[field.name] ?? ""}\n`, `${title || template.name}\n\n`) : "";

  const runGenerate = () => {
    if (!template) return;
    generate.mutate(
      { document_type: template.document_type, title: form.getValues("title") || template.name, fields, save: true },
      {
        onSuccess: (data) => {
          notify({ title: "Document generated", tone: "success" });
          setStep(4);
          if (data.document) window.setTimeout(() => navigate(`/documents/${data.document!.id}`), 900);
        },
      },
    );
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="grid gap-6">
      <SectionHeader eyebrow="Document automation" title="Document Generator" description="Generate compliant legal documents through a focused, multi-step workflow." />

      <Card className="p-4">
        <div className="grid gap-3 sm:grid-cols-5">
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

      <Card className="min-h-[520px] p-6">
        {templates.isLoading ? <Skeleton className="h-80" /> : null}
        {step === 0 && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {templates.data?.results.map((item) => (
              <button
                key={item.id}
                onClick={() => setTemplateType(item.document_type)}
                className={`rounded-lg border p-5 text-left transition ${template?.document_type === item.document_type ? "border-teal-600 bg-teal-50 dark:border-teal-400 dark:bg-teal-950" : "border-slate-200 hover:border-slate-300 dark:border-slate-800 dark:hover:border-slate-700"}`}
              >
                <FileText className="mb-4 text-teal-700 dark:text-teal-300" size={24} />
                <h3 className="font-semibold text-slate-950 dark:text-white">{item.name}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{item.description}</p>
                <Badge tone="slate">{titleize(item.document_type)}</Badge>
              </button>
            ))}
          </div>
        )}

        {step === 1 && template && (
          <div className="mx-auto grid max-w-3xl gap-5">
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

        {step === 2 && (
          <div className="mx-auto max-w-4xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Preview</h2>
              <Badge tone="blue">{template?.name}</Badge>
            </div>
            <pre className="min-h-96 whitespace-pre-wrap rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm leading-7 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300">{preview}</pre>
          </div>
        )}

        {step === 3 && (
          <div className="grid min-h-80 place-items-center text-center">
            <div>
              <WandSparkles className="mx-auto text-teal-700 dark:text-teal-300" size={40} />
              <h2 className="mt-4 text-xl font-semibold text-slate-950 dark:text-white">Ready to generate</h2>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">The document will be saved and versioned automatically.</p>
              <Button className="mt-5" disabled={generate.isPending} onClick={runGenerate} icon={<WandSparkles size={16} />}>
                {generate.isPending ? "Generating..." : "Generate document"}
              </Button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="grid min-h-80 place-items-center text-center">
            <div>
              <Save className="mx-auto text-emerald-600" size={42} />
              <h2 className="mt-4 text-xl font-semibold text-slate-950 dark:text-white">Document saved</h2>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Opening the editor now.</p>
            </div>
          </div>
        )}
      </Card>

      <div className="flex justify-between">
        <Button variant="secondary" disabled={step === 0 || generate.isPending} onClick={() => setStep((value) => Math.max(0, value - 1))} icon={<ChevronLeft size={16} />}>Back</Button>
        {step < 3 ? (
          <Button disabled={!canContinue} onClick={async () => {
            if (step === 1) {
              const ok = await form.trigger();
              if (!ok || missing.length) return;
            }
            setStep((value) => value + 1);
          }}>
            Continue <ChevronRight size={16} />
          </Button>
        ) : null}
      </div>
    </motion.div>
  );
}
