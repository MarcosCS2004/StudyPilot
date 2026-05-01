import type { Metadata } from "next";
import ExamAutopsyReport from "@/components/ExamAutopsyReport";

export const metadata: Metadata = {
  title: "Autopsia de Examen",
  description: "Sube un examen suspendido y recibe un análisis IA detallado de cada error con su causa raíz.",
};

export default function ExamAutopsyPage() {
  return <ExamAutopsyReport />;
}
