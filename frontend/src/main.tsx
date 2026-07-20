import React, { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { AppLayout } from "./components/layout/AppLayout";
import { ErrorBoundary } from "./components/system/ErrorBoundary";
import { PageLoader } from "./components/system/PageLoader";
import { ToastProvider } from "./components/system/Toast";
import { ThemeProvider } from "./contexts/theme";
import { queryClient } from "./lib/queryClient";
import "./styles.css";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const DocumentsPage = lazy(() => import("./pages/DocumentsPage"));
const GeneratorPage = lazy(() => import("./pages/GeneratorPage"));
const EditorPage = lazy(() => import("./pages/EditorPage"));
const ComparePage = lazy(() => import("./pages/ComparePage"));

function App() {
  return (
    <React.StrictMode>
      <ErrorBoundary>
        <ThemeProvider>
          <ToastProvider>
            <QueryClientProvider client={queryClient}>
              <BrowserRouter>
                <AnimatePresence mode="wait">
                  <Routes>
                    <Route element={<AppLayout />}>
                      <Route index element={<Navigate to="/dashboard" replace />} />
                      <Route path="dashboard" element={<Suspense fallback={<PageLoader />}><DashboardPage /></Suspense>} />
                      <Route path="documents" element={<Suspense fallback={<PageLoader />}><DocumentsPage /></Suspense>} />
                      <Route path="documents/:documentId" element={<Suspense fallback={<PageLoader />}><EditorPage /></Suspense>} />
                      <Route path="generate" element={<Suspense fallback={<PageLoader />}><GeneratorPage /></Suspense>} />
                      <Route path="compare" element={<Suspense fallback={<PageLoader />}><ComparePage /></Suspense>} />
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Route>
                  </Routes>
                </AnimatePresence>
              </BrowserRouter>
            </QueryClientProvider>
          </ToastProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </React.StrictMode>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
