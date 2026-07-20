import { useMemo, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  ChevronLeft,
  ChevronRight,
  FileDiff,
  FileText,
  Gauge,
  Menu,
  Moon,
  PanelLeftClose,
  Plus,
  Search,
  Sun,
  WandSparkles,
  X,
} from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "../ui/Button";
import { Tooltip } from "../ui/Tooltip";
import { Input } from "../ui/Form";
import { Badge } from "../ui/Surface";
import { useTheme } from "../../contexts/theme";
import { cn } from "../../lib/utils";
import { GrovynMark } from "../brand/GrovynMark";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/documents", label: "Legal Documents", icon: FileText },
  { to: "/generate", label: "Document Generator", icon: WandSparkles },
  { to: "/compare", label: "Compare Documents", icon: FileDiff },
];

function Sidebar({ collapsed, onToggle, mobileClose }: { collapsed: boolean; onToggle: () => void; mobileClose?: () => void }) {
  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-slate-200 bg-white/92 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/92",
        collapsed ? "w-[76px]" : "w-[304px]",
      )}
    >
      <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-4 dark:border-slate-800">
        <GrovynMark />
        {!collapsed ? (
          <div className="flex min-w-0 items-center">
            <p className="truncate whitespace-nowrap text-sm font-bold text-slate-950 dark:text-white">Legal Document Platform</p>
          </div>
        ) : null}
        <Button variant="ghost" size="icon" className="ml-auto hidden lg:inline-flex" onClick={onToggle} aria-label="Toggle sidebar">
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </Button>
        {mobileClose ? (
          <Button variant="ghost" size="icon" className="ml-auto lg:hidden" onClick={mobileClose} aria-label="Close menu">
            <X size={18} />
          </Button>
        ) : null}
      </div>

      <nav className="grid gap-1.5 p-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Tooltip key={item.to} label={collapsed ? item.label : ""}>
              <NavLink
                to={item.to}
                onClick={mobileClose}
                className={({ isActive }) =>
                  cn(
                    "flex h-11 w-full items-center gap-3 rounded-md px-3 text-sm font-medium transition",
                    isActive
                      ? "bg-slate-950 text-white dark:bg-white dark:text-slate-950"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-400 dark:hover:bg-slate-900 dark:hover:text-white",
                    collapsed && "justify-center px-0",
                  )
                }
              >
                <Icon size={18} className="shrink-0" />
                {!collapsed ? <span>{item.label}</span> : null}
              </NavLink>
            </Tooltip>
          );
        })}
      </nav>

      {!collapsed ? (
        <div className="mt-auto p-3">
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
            <Badge tone="teal">AI enabled</Badge>
            <p className="mt-3 text-sm font-semibold text-slate-950 dark:text-white">Gemini document review</p>
            <p className="mt-1 text-xs leading-5 text-slate-600 dark:text-slate-400">Clause explanations, risk analysis, and version summaries are available inside each document.</p>
          </div>
        </div>
      ) : null}
    </aside>
  );
}

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [query, setQuery] = useState("");
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const pageTitle = useMemo(
    () => navItems.find((item) => location.pathname === item.to || location.pathname.startsWith(`${item.to}/`))?.label ?? "Dashboard",
    [location.pathname],
  );

  const submitSearch = (event: React.FormEvent) => {
    event.preventDefault();
    navigate(`/documents?search=${encodeURIComponent(query)}`);
  };

  return (
    <div className="flex min-h-screen text-slate-950 dark:text-white">
      <div className="sticky top-0 hidden h-screen lg:block">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
      </div>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 bg-slate-950/50 backdrop-blur-sm lg:hidden">
          <motion.div initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }} className="h-full">
            <Sidebar collapsed={false} onToggle={() => undefined} mobileClose={() => setMobileOpen(false)} />
          </motion.div>
        </div>
      ) : null}

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-40 flex h-16 items-center gap-3 border-b border-slate-200 bg-white/86 px-4 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/82 sm:px-6">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
            <Menu size={20} />
          </Button>
          <Button variant="ghost" size="icon" className="hidden lg:inline-flex" onClick={() => setCollapsed((value) => !value)} aria-label="Collapse sidebar">
            <PanelLeftClose size={19} />
          </Button>
          <div className="flex min-w-0 items-center gap-3">
            <GrovynMark className="hidden h-8 sm:block lg:hidden" />
            <div className="flex min-w-0 items-center">
              <h1 className="truncate whitespace-nowrap text-sm font-bold text-slate-950 dark:text-white sm:text-base">{pageTitle}</h1>
            </div>
          </div>

          <form onSubmit={submitSearch} className="ml-auto hidden w-full max-w-xl items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-2 dark:border-slate-800 dark:bg-slate-900 md:flex">
            <Search size={17} className="text-slate-400" />
            <Input
              className="h-9 border-0 bg-transparent px-0 shadow-none focus:border-0"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search agreements, clauses, parties"
            />
          </form>

          <div className="flex items-center gap-2">
            <Tooltip label="Create document" align="end">
              <Button variant="secondary" size="icon" onClick={() => navigate("/generate")} aria-label="Create document">
                <Plus size={18} />
              </Button>
            </Tooltip>
            <Tooltip label={theme === "dark" ? "Use light theme" : "Use dark theme"} align="end">
              <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
                {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              </Button>
            </Tooltip>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1480px] px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
