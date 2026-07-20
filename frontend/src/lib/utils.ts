import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(value?: string) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export function formatDateTime(value?: string) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function titleize(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char: string) => char.toUpperCase());
}

export function wordCount(value: string) {
  return value.trim() ? value.trim().split(/\s+/).length : 0;
}

export function truncate(value: string, length = 120) {
  return value.length > length ? `${value.slice(0, length - 1)}...` : value;
}
