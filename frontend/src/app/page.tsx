import type { Metadata } from "next";
import Dashboard from "@/components/Dashboard";

export const metadata: Metadata = {
  title: "Mi Progreso",
  description: "Visualiza tu dominio por asignatura, racha de estudio y estadísticas personales.",
};

export default function DashboardPage() {
  return <Dashboard />;
}
