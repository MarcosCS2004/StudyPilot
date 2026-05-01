"use client";

/**
 * Dashboard.tsx
 * ─────────────────────────────────────────────────────────────────
 * StudyPilot – Progress Dashboard
 * Renders: Streak counter hero widget + subject mastery cards.
 * Data: TanStack Query → GET /api/v1/profile/progress
 * ─────────────────────────────────────────────────────────────────
 */

import { useQuery } from "@tanstack/react-query";
import {
  Flame,
  BookOpen,
  TrendingUp,
  Zap,
  ChevronRight,
  Star,
  Target,
  RefreshCcw,
} from "lucide-react";
import Link from "next/link";
import { profileApi } from "@/lib/api";
import {
  cn,
  getDifficultyLabel,
  getDifficultyClass,
  formatPct,
} from "@/lib/utils";
import type { SubjectProgress, TopicLevel } from "@/types/api";

// ─── Skeleton Components ───────────────────────────────────────────

function StreakSkeleton() {
  return (
    <div className="glass-card p-8 flex flex-col items-center gap-4 animate-pulse">
      <div className="skeleton w-20 h-20 rounded-full" />
      <div className="skeleton w-32 h-8 rounded-lg" />
      <div className="skeleton w-48 h-4 rounded-md" />
    </div>
  );
}

function SubjectCardSkeleton() {
  return (
    <div className="glass-card p-6 space-y-4 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="skeleton w-40 h-6 rounded-md" />
        <div className="skeleton w-12 h-5 rounded-full" />
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="space-y-2">
          <div className="flex justify-between">
            <div className="skeleton w-32 h-4 rounded-md" />
            <div className="skeleton w-10 h-4 rounded-md" />
          </div>
          <div className="skeleton w-full h-2 rounded-full" />
        </div>
      ))}
    </div>
  );
}

// ─── Streak Hero Widget ────────────────────────────────────────────

interface StreakWidgetProps {
  racha_dias: number;
  xp_total: number;
  nombre: string;
}

function StreakWidget({ racha_dias, xp_total, nombre }: StreakWidgetProps) {
  const isOnFire = racha_dias >= 3;
  const flameCount = Math.min(racha_dias, 7);

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border p-8",
        "flex flex-col items-center gap-3 text-center",
        "transition-all duration-500",
        isOnFire
          ? "border-amber-500/40 bg-gradient-to-br from-amber-500/10 via-card/60 to-rose-500/5 glow-amber"
          : "glass-card"
      )}
    >
      {/* Background glow rings */}
      {isOnFire && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-10 left-1/2 -translate-x-1/2 w-56 h-56 rounded-full bg-amber-500/10 blur-3xl" />
        </div>
      )}

      {/* Greeting */}
      <p className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">
        Bienvenido de nuevo
      </p>
      <h2 className="text-2xl font-display font-bold text-foreground">
        {nombre.split(" ")[0]} 👋
      </h2>

      {/* Flame stack */}
      <div className="flex gap-0.5 my-1" aria-label={`${racha_dias} días de racha`}>
        {Array.from({ length: flameCount }).map((_, i) => (
          <Flame
            key={i}
            className={cn(
              "transition-all duration-300",
              i < racha_dias
                ? "text-amber-400 drop-shadow-[0_0_6px_rgba(251,191,36,0.7)]"
                : "text-muted/40",
              i === flameCount - 1 && isOnFire
                ? "scale-125 animate-pulse-scale"
                : ""
            )}
            style={{ width: 28 + i * 2, height: 28 + i * 2 }}
            fill="currentColor"
          />
        ))}
      </div>

      {/* Counter */}
      <div className="flex items-baseline gap-1">
        <span
          className={cn(
            "text-6xl font-display font-extrabold tabular-nums animate-streak-pop",
            isOnFire ? "text-gradient" : "text-foreground"
          )}
        >
          {racha_dias}
        </span>
        <span className="text-xl font-semibold text-muted-foreground">
          días
        </span>
      </div>

      <p className="text-sm text-muted-foreground max-w-[200px]">
        {racha_dias === 0
          ? "¡Hoy es un buen día para empezar!"
          : racha_dias < 3
          ? "¡Sigue así, la racha crece!"
          : racha_dias < 7
          ? "🔥 ¡Estás en racha! No lo pierdas."
          : "🚀 ¡Eres imparable! Semana perfecta."}
      </p>

      {/* XP badge */}
      <div className="flex items-center gap-2 mt-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
        <Zap className="w-4 h-4 text-primary" fill="currentColor" />
        <span className="text-sm font-semibold text-primary">
          {xp_total.toLocaleString()} XP totales
        </span>
      </div>

      {/* CTA */}
      <Link href="/study" className="btn-primary mt-2 w-full max-w-[200px]">
        <Target className="w-4 h-4" />
        Estudiar ahora
      </Link>
    </div>
  );
}

// ─── Topic Row ─────────────────────────────────────────────────────

function TopicRow({ topic }: { topic: TopicLevel }) {
  const pct = (topic.nivel / 10) * 100;
  const barColor =
    topic.nivel <= 3
      ? "from-emerald-500 to-emerald-400"
      : topic.nivel <= 6
      ? "from-amber-500 to-amber-400"
      : "from-primary to-accent";

  return (
    <div className="group space-y-1.5">
      <div className="flex items-center justify-between">
        <span className="text-sm text-foreground/90 font-medium truncate max-w-[180px]">
          {topic.nombre_tema}
        </span>
        <div className="flex items-center gap-2 shrink-0">
          <span
            className={cn(
              getDifficultyClass(topic.nivel),
              "text-[10px] px-1.5 py-0.5"
            )}
          >
            {getDifficultyLabel(topic.nivel)}
          </span>
          <span className="text-xs text-muted-foreground tabular-nums">
            {formatPct(topic.pct_acierto)}
          </span>
        </div>
      </div>
      <div className="level-bar">
        <div
          className={cn("level-bar-fill bg-gradient-to-r", barColor)}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={topic.nivel}
          aria-valuemin={0}
          aria-valuemax={10}
        />
      </div>
    </div>
  );
}

// ─── Subject Card ──────────────────────────────────────────────────

function SubjectCard({ subject }: { subject: SubjectProgress }) {
  const avgLevel =
    subject.temas.length > 0
      ? subject.temas.reduce((a, t) => a + t.nivel, 0) / subject.temas.length
      : 0;
  const avgAcierto =
    subject.temas.length > 0
      ? subject.temas.reduce((a, t) => a + t.pct_acierto, 0) /
        subject.temas.length
      : 0;

  return (
    <article className="glass-card-hover p-6 space-y-4 animate-fade-in-up">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0">
            <BookOpen className="w-4.5 h-4.5 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground leading-tight">
              {subject.nombre_asignatura}
            </h3>
            <p className="text-xs text-muted-foreground">
              {subject.temas.length} temas
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          <Star className="w-3.5 h-3.5 text-amber-400" fill="currentColor" />
          <span className="text-sm font-bold text-foreground">
            {avgLevel.toFixed(1)}
          </span>
          <span className="text-xs text-muted-foreground">/ 10</span>
        </div>
      </div>

      {/* Overall accuracy bar */}
      <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border border-border/40">
        <TrendingUp className="w-4 h-4 text-emerald-400 shrink-0" />
        <div className="flex-1 level-bar">
          <div
            className="level-bar-fill bg-gradient-to-r from-emerald-500 to-emerald-400"
            style={{ width: `${avgAcierto}%` }}
          />
        </div>
        <span className="text-xs font-semibold text-emerald-400 tabular-nums">
          {formatPct(avgAcierto)}
        </span>
      </div>

      {/* Topics list */}
      <div className="space-y-3">
        {subject.temas.map((t) => (
          <TopicRow key={t.nombre_tema} topic={t} />
        ))}
      </div>

      {/* Action */}
      <Link
        href={`/study?asignatura=${subject.asignatura_id}`}
        className="flex items-center justify-between text-xs font-semibold text-primary hover:text-primary/80 transition-colors pt-1"
      >
        <span>Practicar esta asignatura</span>
        <ChevronRight className="w-4 h-4" />
      </Link>
    </article>
  );
}

// ─── Stats Strip ───────────────────────────────────────────────────

function StatsStrip({
  totalAsignaturas,
  totalTemas,
  avgAcierto,
}: {
  totalAsignaturas: number;
  totalTemas: number;
  avgAcierto: number;
}) {
  const items = [
    { label: "Asignaturas", value: totalAsignaturas, icon: BookOpen, color: "text-primary" },
    { label: "Temas activos", value: totalTemas, icon: Target, color: "text-accent" },
    {
      label: "Acierto medio",
      value: `${Math.round(avgAcierto)}%`,
      icon: TrendingUp,
      color: "text-emerald-400",
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-4">
      {items.map(({ label, value, icon: Icon, color }) => (
        <div
          key={label}
          className="glass-card p-4 flex flex-col items-center gap-1 text-center"
        >
          <Icon className={cn("w-5 h-5", color)} />
          <span className="text-xl font-bold font-display text-foreground">
            {value}
          </span>
          <span className="text-xs text-muted-foreground">{label}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Main Component ────────────────────────────────────────────────

export default function Dashboard() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["profile-progress"],
    queryFn: profileApi.getProgress,
    staleTime: 60 * 1000, // 1 min
    refetchOnWindowFocus: false,
  });

  // ── Loading ──
  if (isLoading) {
    return (
      <main className="max-w-5xl mx-auto px-4 py-10 space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <StreakSkeleton />
          <div className="lg:col-span-2 space-y-4">
            <SubjectCardSkeleton />
            <SubjectCardSkeleton />
          </div>
        </div>
      </main>
    );
  }

  // ── Error ──
  if (isError || !data) {
    return (
      <main className="max-w-5xl mx-auto px-4 py-10">
        <div className="glass-card p-8 text-center space-y-4">
          <p className="text-rose-400 font-semibold">
            Error al cargar el progreso
          </p>
          <p className="text-sm text-muted-foreground">
            {error instanceof Error ? error.message : "Error desconocido"}
          </p>
          <button onClick={() => refetch()} className="btn-secondary inline-flex">
            <RefreshCcw className="w-4 h-4" />
            Reintentar
          </button>
        </div>
      </main>
    );
  }

  const totalTemas = data.asignaturas.reduce(
    (acc, a) => acc + a.temas.length,
    0
  );
  const allTopics = data.asignaturas.flatMap((a) => a.temas);
  const avgAcierto =
    allTopics.length > 0
      ? allTopics.reduce((a, t) => a + t.pct_acierto, 0) / allTopics.length
      : 0;

  return (
    <main className="max-w-5xl mx-auto px-4 py-10 space-y-8">
      {/* Page heading */}
      <div className="space-y-1">
        <h1 className="text-3xl font-display font-bold text-gradient">
          Mi Progreso
        </h1>
        <p className="text-muted-foreground text-sm">
          Visualiza tu dominio por asignatura y tema.
        </p>
      </div>

      {/* Stats strip */}
      <StatsStrip
        totalAsignaturas={data.asignaturas.length}
        totalTemas={totalTemas}
        avgAcierto={avgAcierto}
      />

      {/* Main grid: streak + subjects */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Streak Widget (leftmost column on desktop) */}
        <div className="lg:col-span-1">
          <StreakWidget
            racha_dias={data.racha_dias}
            xp_total={data.xp_total}
            nombre={data.nombre}
          />
        </div>

        {/* Subject cards */}
        <div className="lg:col-span-2 space-y-4">
          {data.asignaturas.length === 0 ? (
            <div className="glass-card p-10 flex flex-col items-center gap-4 text-center">
              <BookOpen className="w-12 h-12 text-muted-foreground/40" />
              <p className="text-muted-foreground">
                Aún no tienes asignaturas. ¡Sube tus apuntes para empezar!
              </p>
              <Link href="/upload" className="btn-primary">
                Subir apuntes
              </Link>
            </div>
          ) : (
            data.asignaturas.map((subject, idx) => (
              <div
                key={subject.asignatura_id}
                className={cn(
                  "animate-fade-in-up",
                  idx === 0 && "stagger-1",
                  idx === 1 && "stagger-2",
                  idx === 2 && "stagger-3",
                  idx === 3 && "stagger-4"
                )}
              >
                <SubjectCard subject={subject} />
              </div>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
