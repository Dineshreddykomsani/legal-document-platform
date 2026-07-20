import { forwardRef, type ButtonHTMLAttributes, type AnchorHTMLAttributes, type ReactNode } from "react";
import { cn } from "../../lib/utils";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg" | "icon";

const variants: Record<Variant, string> = {
  primary: "bg-teal-700 text-white shadow-sm shadow-teal-950/10 hover:bg-teal-800 dark:bg-teal-500 dark:text-slate-950 dark:hover:bg-teal-400",
  secondary: "border border-slate-200 bg-white text-slate-800 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800",
  ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white",
  danger: "bg-rose-600 text-white hover:bg-rose-700",
};

const sizes: Record<Size, string> = {
  sm: "h-8 px-3 text-xs",
  md: "h-10 px-4 text-sm",
  lg: "h-11 px-5 text-sm",
  icon: "h-10 w-10 p-0",
};

export function buttonClassName({ variant = "primary", size = "md", className }: { variant?: Variant; size?: Size; className?: string } = {}) {
  return cn(
    "inline-flex shrink-0 items-center justify-center gap-2 rounded-md font-medium no-underline transition disabled:pointer-events-none disabled:opacity-50",
    variants[variant],
    sizes[size],
    className,
  );
}

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  icon?: ReactNode;
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", icon, children, ...props }, ref) => (
    <button
      ref={ref}
      className={buttonClassName({ variant, size, className })}
      {...props}
    >
      {icon}
      {children}
    </button>
  ),
);

type LinkButtonProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  variant?: Variant;
  size?: Size;
  icon?: ReactNode;
};

export function LinkButton({ className, variant = "primary", size = "md", icon, children, ...props }: LinkButtonProps) {
  return (
    <a
      className={buttonClassName({ variant, size, className })}
      {...props}
    >
      {icon}
      {children}
    </a>
  );
}
