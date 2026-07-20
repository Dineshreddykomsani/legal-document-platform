import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "../ui/Button";

type State = { hasError: boolean };

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <div className="grid min-h-screen place-items-center bg-slate-50 p-6 text-slate-950 dark:bg-slate-950 dark:text-white">
        <div className="max-w-md rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-300">
            <AlertTriangle size={22} />
          </div>
          <h1 className="text-lg font-semibold">Something needs attention</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">The application could not render. Refresh and try again.</p>
          <Button className="mt-5" onClick={() => window.location.reload()}>
            Refresh application
          </Button>
        </div>
      </div>
    );
  }
}
