import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

type Toast = { id: number; title: string; tone: "success" | "error" };
const ToastContext = createContext<{ notify: (toast: Omit<Toast, "id">) => void } | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const notify = useCallback((toast: Omit<Toast, "id">) => {
    const id = Date.now();
    setToasts((current) => [...current, { ...toast, id }]);
    window.setTimeout(() => setToasts((current) => current.filter((item) => item.id !== id)), 4200);
  }, []);
  const value = useMemo(() => ({ notify }), [notify]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed right-4 top-4 z-[60] grid w-[calc(100%-2rem)] gap-2 sm:w-96">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: -10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.98 }}
              className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium text-slate-900 shadow-xl dark:border-slate-800 dark:bg-slate-900 dark:text-white"
            >
              {toast.tone === "success" ? <CheckCircle2 className="text-emerald-600" size={20} /> : <XCircle className="text-rose-600" size={20} />}
              {toast.title}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used within ToastProvider");
  return context;
}
