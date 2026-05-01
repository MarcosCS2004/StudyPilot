"use client";

/**
 * StudySession.tsx
 * ─────────────────────────────────────────────────────────────────
 * StudyPilot – Adaptive Study Session
 * Flow:
 *   1. Fetch next question   → GET  /api/v1/study/next-question
 *   2. Student selects answer → local state
 *   3. Submit answer         → POST /api/v1/study/answer
 *   4. Show feedback modal (blocks navigation until dismissed)
 *   5. Load next question
 *
 * Skeletons active during LLM generation (p95 < 3 s).
 * ─────────────────────────────────────────────────────────────────
 */

import { useState, useCallback, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  XCircle,
  ChevronRight,
  AlertCircle,
  BookOpen,
  Brain,
  TrendingUp,
  Zap,
  Loader2,
  RefreshCcw,
  Lock,
} from "lucide-react";
import { studyApi } from "@/lib/api";
import { cn, getDifficultyLabel, getDifficultyClass } from "@/lib/utils";
import type {
  NextQuestionResponse,
  AnswerResponse,
} from "@/types/api";

// ─── Types ─────────────────────────────────────────────────────────

type AnswerKey = "A" | "B" | "C" | "D";

interface SessionState {
  selected: AnswerKey | null;
  feedback: AnswerResponse | null;
  feedbackRead: boolean;
  questionCount: number;
  correctCount: number;
  totalXP: number;
}

const INITIAL_STATE: SessionState = {
  selected: null,
  feedback: null,
  feedbackRead: false,
  questionCount: 0,
  correctCount: 0,
  totalXP: 0,
};

// ─── Skeleton ──────────────────────────────────────────────────────

function QuestionSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div className="skeleton w-28 h-5 rounded-full" />
        <div className="skeleton w-20 h-5 rounded-full" />
      </div>
      {/* Enunciado */}
      <div className="glass-card p-6 space-y-3">
        <div className="skeleton w-3/4 h-6 rounded-lg" />
        <div className="skeleton w-full h-4 rounded-md" />
        <div className="skeleton w-5/6 h-4 rounded-md" />
      </div>
      {/* Options */}
      {["A", "B", "C", "D"].map((k) => (
        <div key={k} className="skeleton w-full h-14 rounded-xl" />
      ))}
    </div>
  );
}

// ─── Session Stats Bar ─────────────────────────────────────────────

function SessionStatsBar({
  questionCount,
  correctCount,
  totalXP,
}: Pick<SessionState, "questionCount" | "correctCount" | "totalXP">) {
  const accuracy =
    questionCount > 0 ? Math.round((correctCount / questionCount) * 100) : 0;

  return (
    <div className="flex items-center gap-4 text-xs text-muted-foreground font-medium">
      <span className="flex items-center gap-1">
        <Brain className="w-3.5 h-3.5 text-primary" />
        {questionCount} preguntas
      </span>
      <span className="flex items-center gap-1">
        <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
        {accuracy}% acierto
      </span>
      <span className="flex items-center gap-1">
        <Zap className="w-3.5 h-3.5 text-amber-400" fill="currentColor" />
        +{totalXP} XP
      </span>
    </div>
  );
}

// ─── Option Button ─────────────────────────────────────────────────

interface OptionButtonProps {
  letter: AnswerKey;
  text: string;
  selected: AnswerKey | null;
  feedback: AnswerResponse | null;
  onSelect: (key: AnswerKey) => void;
  disabled: boolean;
}

function OptionButton({
  letter,
  text,
  selected,
  feedback,
  onSelect,
  disabled,
}: OptionButtonProps) {
  const isSelected = selected === letter;
  const hasFeedback = feedback !== null;
  const isCorrect = hasFeedback && feedback.respuesta_correcta === letter;
  const isWrong =
    hasFeedback && isSelected && !feedback.correcto;

  const cls = cn(
    "answer-btn",
    !hasFeedback && isSelected && "answer-btn-selected",
    hasFeedback && isCorrect && "answer-btn-correct",
    hasFeedback && isWrong && "answer-btn-wrong",
    hasFeedback && !isCorrect && !isSelected && "answer-btn-disabled",
    disabled && !hasFeedback && "opacity-60 cursor-not-allowed"
  );

  return (
    <button
      id={`option-${letter}`}
      className={cls}
      onClick={() => !disabled && !hasFeedback && onSelect(letter)}
      disabled={disabled || hasFeedback !== null}
      aria-pressed={isSelected}
    >
      <div className="flex items-center gap-3">
        {/* Letter badge */}
        <span
          className={cn(
            "w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 border",
            !hasFeedback && isSelected
              ? "bg-primary text-white border-primary"
              : !hasFeedback
              ? "bg-muted border-border text-muted-foreground"
              : isCorrect
              ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-400"
              : isWrong
              ? "bg-rose-500/20 border-rose-500/50 text-rose-400"
              : "bg-muted border-border text-muted-foreground"
          )}
        >
          {letter}
        </span>
        <span className="flex-1 text-left leading-snug">{text}</span>
        {/* Result icon */}
        {hasFeedback && isCorrect && (
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
        )}
        {hasFeedback && isWrong && (
          <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
        )}
      </div>
    </button>
  );
}

// ─── Feedback Panel ────────────────────────────────────────────────

interface FeedbackPanelProps {
  feedback: AnswerResponse;
  question: NextQuestionResponse;
  onContinue: () => void;
  isLoadingNext: boolean;
}

function FeedbackPanel({
  feedback,
  question,
  onContinue,
  isLoadingNext,
}: FeedbackPanelProps) {
  const correct = feedback.correcto;

  return (
    <div
      className={cn(
        "mt-6 rounded-2xl border p-6 space-y-4 animate-fade-in-up",
        correct
          ? "border-emerald-500/40 bg-emerald-500/5"
          : "border-rose-500/40 bg-rose-500/5"
      )}
      role="alert"
      aria-live="polite"
    >
      {/* Result header */}
      <div className="flex items-center gap-3">
        {correct ? (
          <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
        ) : (
          <XCircle className="w-6 h-6 text-rose-400 shrink-0" />
        )}
        <div>
          <p
            className={cn(
              "font-bold text-lg",
              correct ? "text-emerald-400" : "text-rose-400"
            )}
          >
            {correct ? "¡Correcto! 🎉" : "Incorrecto"}
          </p>
          {!correct && (
            <p className="text-sm text-muted-foreground">
              La respuesta correcta era{" "}
              <span className="font-semibold text-foreground">
                {feedback.respuesta_correcta}:{" "}
                {
                  question.opciones[
                    feedback.respuesta_correcta as keyof typeof question.opciones
                  ]
                }
              </span>
            </p>
          )}
        </div>
      </div>

      {/* LLM Explanation */}
      <div className="p-4 rounded-xl bg-card/60 border border-border/60 space-y-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          <Brain className="w-3.5 h-3.5" />
          Explicación del tutor
        </div>
        <p className="text-sm text-foreground/90 leading-relaxed">
          {feedback.explicacion}
        </p>
      </div>

      {/* Level update + XP */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 text-sm">
          <TrendingUp className="w-4 h-4 text-primary" />
          <span className="text-muted-foreground">Nuevo nivel en </span>
          <span className="font-semibold text-foreground">{question.tema}</span>
          <span
            className={cn(
              "font-bold",
              feedback.nuevo_nivel_tema >= 7
                ? "text-primary"
                : feedback.nuevo_nivel_tema >= 4
                ? "text-amber-400"
                : "text-emerald-400"
            )}
          >
            {feedback.nuevo_nivel_tema}/10
          </span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20">
          <Zap className="w-3.5 h-3.5 text-amber-400" fill="currentColor" />
          <span className="text-xs font-bold text-amber-400">
            +{feedback.xp_ganado} XP
          </span>
        </div>
      </div>

      {/* Lock notice + Continue button */}
      <div className="flex items-center gap-3 pt-1">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground flex-1">
          <Lock className="w-3 h-3" />
          Lee el feedback antes de continuar
        </div>
        <button
          id="btn-continue-study"
          className="btn-primary"
          onClick={onContinue}
          disabled={isLoadingNext}
        >
          {isLoadingNext ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              Siguiente pregunta
              <ChevronRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────

interface StudySessionProps {
  asignaturaId?: string;
}

export default function StudySession({ asignaturaId }: StudySessionProps) {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<SessionState>(INITIAL_STATE);

  // ── Fetch next question ──────────────────────────────────────────
  const {
    data: question,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["next-question", asignaturaId],
    queryFn: () => studyApi.getNextQuestion(asignaturaId),
    staleTime: Infinity,
    refetchOnWindowFocus: false,
    enabled: true,
  });

  // Reset selection when a new question arrives
  useEffect(() => {
    if (question) {
      setSession((s) => ({ ...s, selected: null, feedback: null }));
    }
  }, [question?.question_id]);

  // ── Submit answer ────────────────────────────────────────────────
  const answerMutation = useMutation({
    mutationFn: studyApi.submitAnswer,
    onSuccess: (data) => {
      setSession((s) => ({
        ...s,
        feedback: data,
        questionCount: s.questionCount + 1,
        correctCount: s.correctCount + (data.correcto ? 1 : 0),
        totalXP: s.totalXP + data.xp_ganado,
      }));
    },
  });

  // ── Handlers ─────────────────────────────────────────────────────
  const handleSelect = useCallback(
    (key: AnswerKey) => {
      if (session.feedback || answerMutation.isPending) return;
      setSession((s) => ({ ...s, selected: key }));

      if (!question) return;
      answerMutation.mutate({
        question_id: question.question_id,
        respuesta: key,
      });
    },
    [session.feedback, answerMutation, question]
  );

  const handleNextQuestion = useCallback(() => {
    // Invalidate so TanStack refetches with fresh question
    queryClient.invalidateQueries({ queryKey: ["next-question", asignaturaId] });
  }, [queryClient, asignaturaId]);

  // ── Loading state (LLM generating) ──────────────────────────────
  if (isLoading || isFetching) {
    return (
      <section className="max-w-2xl mx-auto px-4 py-10">
        <div className="flex items-center gap-2 mb-6 text-sm text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin text-primary" />
          El tutor IA está preparando tu pregunta…
        </div>
        <QuestionSkeleton />
      </section>
    );
  }

  // ── Error state ──────────────────────────────────────────────────
  if (isError || !question) {
    return (
      <section className="max-w-2xl mx-auto px-4 py-10">
        <div className="glass-card p-8 text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
          <p className="font-semibold text-rose-400">
            No se pudo cargar la pregunta
          </p>
          <p className="text-sm text-muted-foreground">
            {error instanceof Error ? error.message : "Error desconocido"}
          </p>
          <button onClick={() => refetch()} className="btn-secondary">
            <RefreshCcw className="w-4 h-4" />
            Reintentar
          </button>
        </div>
      </section>
    );
  }

  const isSubmitting = answerMutation.isPending;

  return (
    <section className="max-w-2xl mx-auto px-4 py-10 space-y-6">
      {/* Top bar */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-primary" />
          <span className="text-sm font-semibold text-foreground">
            {question.asignatura}
          </span>
          <span className="text-muted-foreground text-sm">·</span>
          <span className="text-sm text-muted-foreground">{question.tema}</span>
        </div>
        <SessionStatsBar
          questionCount={session.questionCount}
          correctCount={session.correctCount}
          totalXP={session.totalXP}
        />
      </div>

      {/* Question card */}
      <article className="glass-card p-6 space-y-3 animate-fade-in-up">
        {/* Difficulty badge */}
        <div className="flex items-center justify-between">
          <span
            className={cn(
              getDifficultyClass(question.nivel_dificultad),
              "text-xs"
            )}
          >
            {getDifficultyLabel(question.nivel_dificultad)} · Nivel{" "}
            {question.nivel_dificultad}
          </span>
          <span className="text-xs text-muted-foreground font-mono">
            #{question.question_id.slice(0, 8)}
          </span>
        </div>

        {/* Enunciado */}
        <h2 className="text-base font-semibold text-foreground leading-relaxed">
          {question.enunciado}
        </h2>
      </article>

      {/* Answer options */}
      <div className="space-y-3" role="group" aria-label="Opciones de respuesta">
        {(["A", "B", "C", "D"] as AnswerKey[]).map((letter) => (
          <OptionButton
            key={letter}
            letter={letter}
            text={question.opciones[letter]}
            selected={session.selected}
            feedback={session.feedback}
            onSelect={handleSelect}
            disabled={isSubmitting}
          />
        ))}
      </div>

      {/* Submitting spinner (between select → feedback) */}
      {isSubmitting && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground animate-fade-in-up">
          <Loader2 className="w-4 h-4 animate-spin text-primary" />
          Evaluando tu respuesta…
        </div>
      )}

      {/* Error from mutation */}
      {answerMutation.isError && (
        <div className="flex items-center gap-2 text-sm text-rose-400 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {answerMutation.error instanceof Error
            ? answerMutation.error.message
            : "Error al enviar la respuesta"}
        </div>
      )}

      {/* Feedback Panel – blocks until read */}
      {session.feedback && !isSubmitting && (
        <FeedbackPanel
          feedback={session.feedback}
          question={question}
          onContinue={handleNextQuestion}
          isLoadingNext={isFetching}
        />
      )}
    </section>
  );
}
