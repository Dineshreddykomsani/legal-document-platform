import { forwardRef, type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

const field =
  "w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-950 shadow-sm transition placeholder:text-slate-400 hover:border-slate-300 focus:border-teal-600 focus:outline-none dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500 dark:hover:border-slate-600";

export function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <label className="grid gap-1.5 text-sm font-medium text-slate-700 dark:text-slate-200">
      <span>{label}</span>
      {children}
      {error ? <span className="text-xs font-medium text-rose-600 dark:text-rose-400">{error}</span> : null}
    </label>
  );
}

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input ref={ref} className={cn(field, "h-10", className)} {...props} />
));

export const DatePicker = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>((props, ref) => (
  <Input ref={ref} type="date" {...props} />
));

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(({ className, ...props }, ref) => (
  <textarea ref={ref} className={cn(field, "min-h-28 resize-y py-3 leading-6", className)} {...props} />
));

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(({ className, children, ...props }, ref) => (
  <select ref={ref} className={cn(field, "h-10 appearance-auto", className)} {...props}>
    {children}
  </select>
));
