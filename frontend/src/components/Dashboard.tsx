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

// ─── Welcome Widget ────────────────────────────────────────────

interface WelcomeWidgetProps {
  nombre: string;
}

function WelcomeWidget({ nombre }: WelcomeWidgetProps) {
  return (
    <div className="glass-card p-8 flex flex-col items-center gap-2 text-center">
      <p className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">
        Bienvenido de nuevo
      </p>
      <h2 className="text-2xl font-display font-bold text-foreground">
        {nombre.split(" ")[0]} 👋
      </h2>
      <p className="text-sm text-muted-foreground max-w-[250px] mt-2">
        Continúa con tus estudios y mejora tu dominio de las asignaturas.
      </p>
      <Link href="/study" className="btn-primary mt-4 w-full max-w-[200px]">
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
    <div className="group py-1 border-b border-border/30 last:border-0">
      <div className="flex items-center justify-between">
        <span className="text-sm text-foreground/90 font-medium truncate max-w-[180px]">
          {topic.nombre_tema}
        </span>
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex flex-col items-end">
            <span className="text-xs font-bold text-foreground tabular-nums">
              {formatPct(topic.pct_acierto)}
            </span>
            <span className="text-[10px] text-muted-foreground uppercase tracking-tight">
              Acierto
            </span>
          </div>
        </div>
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
        <div className="flex flex-col items-end shrink-0">
          <span className="text-sm font-bold text-foreground">
            {formatPct(avgAcierto)}
          </span>
          <span className="text-[10px] text-muted-foreground uppercase">Promedio</span>
        </div>
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
        {/* Welcome Widget (leftmost column on desktop) */}
        <div className="lg:col-span-1">
          <WelcomeWidget
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
