import { cn } from "../../lib/utils";

export function GrovynMark({ className }: { className?: string }) {
  return (
    <img
      src="/grovyn-logo.png"
      alt=""
      className={cn(
        "h-9 w-auto shrink-0 object-contain",
        className,
      )}
      aria-hidden="true"
    />
  );
}
