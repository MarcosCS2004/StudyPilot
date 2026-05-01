import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getDifficultyLabel(level: number): string {
  if (level <= 3) return "Básico";
  if (level <= 6) return "Intermedio";
  return "Avanzado";
}

export function getDifficultyClass(level: number): string {
  if (level <= 3) return "badge bg-emerald-500/15 text-emerald-400 border border-emerald-500/25";
  if (level <= 6) return "badge bg-amber-500/15 text-amber-400 border border-amber-500/25";
  return "badge bg-rose-500/15 text-rose-400 border border-rose-500/25";
}

export function getFaultTypeLabel(tipo: string): string {
  const map: Record<string, string> = {
    confusion: "Confusión conceptual",
    laguna:    "Laguna de conocimiento",
    parcial:   "Comprensión parcial",
  };
  return map[tipo] ?? tipo;
}

export function getFaultClass(tipo: string): string {
  const map: Record<string, string> = {
    confusion: "fault-confusion",
    laguna:    "fault-laguna",
    parcial:   "fault-parcial",
  };
  return map[tipo] ?? "badge";
}

export function formatPct(value: number): string {
  return `${Math.round(value)}%`;
}
