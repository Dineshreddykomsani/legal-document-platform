import { Skeleton } from "../ui/Skeleton";

export function PageLoader() {
  return (
    <div className="grid gap-5">
      <Skeleton className="h-20" />
      <div className="grid gap-4 lg:grid-cols-3">
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
      </div>
      <Skeleton className="h-96" />
    </div>
  );
}
