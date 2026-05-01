import type { Metadata } from "next";
import StudySession from "@/components/StudySession";

export const metadata: Metadata = {
  title: "Sesión de Estudio",
  description: "Responde preguntas adaptativas generadas por IA basadas en tus apuntes y nivel actual.",
};

interface StudyPageProps {
  searchParams: { asignatura?: string; session?: string };
}

export default function StudyPage({ searchParams }: StudyPageProps) {
  return (
    <StudySession
      asignaturaId={searchParams.asignatura}
    />
  );
}
