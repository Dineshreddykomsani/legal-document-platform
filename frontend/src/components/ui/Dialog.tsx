import { X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { ReactNode } from "react";
import { Button } from "./Button";

export function Dialog({ open, title, children, onClose }: { open: boolean; title: string; children: ReactNode; onClose: () => void }) {
  return (
    <AnimatePresence>
      {open ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.98, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: 12 }}
            className="w-full max-w-lg rounded-lg border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
              <h2 className="text-base font-semibold text-slate-950 dark:text-white">{title}</h2>
              <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close dialog">
                <X size={18} />
              </Button>
            </div>
            <div className="p-5">{children}</div>
          </motion.div>
        </div>
      ) : null}
    </AnimatePresence>
  );
}

export function Drawer({ open, title, children, onClose }: { open: boolean; title: string; children: ReactNode; onClose: () => void }) {
  return (
    <AnimatePresence>
      {open ? (
        <div className="fixed inset-0 z-50 bg-slate-950/40 backdrop-blur-sm">
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="ml-auto h-full w-full max-w-xl overflow-y-auto border-l border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="sticky top-0 flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4 dark:border-slate-800 dark:bg-slate-900">
              <h2 className="text-base font-semibold text-slate-950 dark:text-white">{title}</h2>
              <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close drawer">
                <X size={18} />
              </Button>
            </div>
            <div className="p-5">{children}</div>
          </motion.aside>
        </div>
      ) : null}
    </AnimatePresence>
  );
}
