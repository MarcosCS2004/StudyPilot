"use client";

import { useState } from "react";
import StudySession from "@/components/StudySession";
import TutorChat from "@/components/TutorChat";
import { Brain, MessageSquare, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface StudyPageProps {
  searchParams: { asignatura?: string; mode?: string };
}

export default function StudyPage({ searchParams }: StudyPageProps) {
  const [mode, setMode] = useState<"test" | "chat">(
    (searchParams.mode as "test" | "chat") || "chat"
  );

  return (
    <main className="min-h-[calc(100vh-4rem)] pt-6 pb-12 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header Section */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-gradient">
            Centro de Aprendizaje IA
          </h1>
          <p className="text-muted-foreground text-sm max-w-lg mx-auto">
            Elige cómo quieres estudiar hoy: mediante preguntas adaptativas o conversando directamente con tu tutor.
          </p>
        </div>

        {/* Mode Selector */}
        <div className="flex justify-center">
          <div className="inline-flex p-1 bg-muted/50 backdrop-blur-sm rounded-xl border border-border/50">
            <button
              onClick={() => setMode("chat")}
              className={cn(
                "flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-semibold transition-all",
                mode === "chat" 
                  ? "bg-primary text-white shadow-lg shadow-primary/20" 
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <MessageSquare className="w-4 h-4" />
              Chat con Tutor
            </button>
            <button
              onClick={() => setMode("test")}
              className={cn(
                "flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-semibold transition-all",
                mode === "test" 
                  ? "bg-primary text-white shadow-lg shadow-primary/20" 
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Brain className="w-4 h-4" />
              Sesión de Test
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="animate-fade-in-up">
          {mode === "chat" ? (
            <div className="space-y-6">
              <div className="bg-primary/5 border border-primary/10 rounded-2xl p-4 flex items-start gap-3">
                <div className="p-2 bg-primary/10 rounded-lg shrink-0">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-primary uppercase tracking-wider mb-1">Modo Chat Activo</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Pregunta cualquier cosa sobre tus materiales. El tutor usará búsqueda semántica (RAG) para encontrar la respuesta exacta en tus documentos.
                  </p>
                </div>
              </div>
              <TutorChat />
            </div>
          ) : (
            <StudySession asignaturaId={searchParams.asignatura} />
          )}
        </div>
      </div>
    </main>
  );
}
