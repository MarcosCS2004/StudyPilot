"use client";

/**
 * ExamAutopsyReport.tsx
 * ─────────────────────────────────────────────────────────────────
 * StudyPilot – Exam Autopsy Upload & Diagnostic Report
 *
 * Sections:
 *   A. UploadCenter  – drag-and-drop PDF/DOCX/JPG + notes upload
 *   B. AutopsyReport – per-error breakdown after exam analysis
 *
 * API:
 *   POST /api/v1/exam-autopsy/upload → ExamAutopsyResponse
 *   POST /api/v1/documents/upload   → UploadResponse
 * ─────────────────────────────────────────────────────────────────
 */

import {
  useState,
  useCallback,
  useRef,
  type DragEvent,
  type ChangeEvent,
} from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Upload,
  FileText,
  Image as ImageIcon,
  File,
  CheckCircle2,
  XCircle,
  Loader2,
  AlertCircle,
  BookOpen,
  Brain,
  ChevronRight,
  ScanLine,
  Link2,
  AlertTriangle,
  Play,
  Trash2,
  Microscope,
} from "lucide-react";
import Link from "next/link";
import { examApi, documentsApi } from "@/lib/api";
import { cn, getFaultTypeLabel, getFaultClass } from "@/lib/utils";
import type { ExamAutopsyResponse, ErrorItem, UploadStatus } from "@/types/api";

// ─── Helpers ───────────────────────────────────────────────────────

function getFileIcon(name: string) {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "pdf") return <FileText className="w-5 h-5 text-rose-400" />;
  if (ext === "docx" || ext === "doc")
    return <FileText className="w-5 h-5 text-primary" />;
  if (["jpg", "jpeg", "png"].includes(ext ?? ""))
    return <ImageIcon className="w-5 h-5 text-emerald-400" />;
  return <File className="w-5 h-5 text-muted-foreground" />;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const ACCEPTED = [".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png"];
const ACCEPTED_MIME = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/msword",
  "image/jpeg",
  "image/png",
];

function isAccepted(file: File) {
  return ACCEPTED_MIME.includes(file.type);
}

// ─── Fault Type Badge ──────────────────────────────────────────────

function FaultBadge({ tipo }: { tipo: string }) {
  return (
    <span className={cn(getFaultClass(tipo), "text-xs")}>
      {getFaultTypeLabel(tipo)}
    </span>
  );
}

// ─── Source Link Box ───────────────────────────────────────────────

function SourceLinkBox({ chunk_source }: { chunk_source: string }) {
  return (
    <div className="mt-3 p-3 rounded-xl border border-primary/25 bg-primary/5 space-y-1.5">
      <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-primary/80">
        <Link2 className="w-3 h-3" />
        Fuente en tus apuntes
      </div>
      <blockquote className="text-xs text-foreground/80 leading-relaxed italic border-l-2 border-primary/40 pl-3">
        "{chunk_source}"
      </blockquote>
    </div>
  );
}

// ─── Single Error Item Card ────────────────────────────────────────

function ErrorItemCard({
  item,
  index,
}: {
  item: ErrorItem;
  index: number;
}) {
  const [expanded, setExpanded] = useState(true);

  return (
    <article
      className={cn(
        "glass-card-hover p-5 space-y-3 animate-fade-in-up",
        `stagger-${Math.min(index + 1, 5)}`
      )}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-muted border border-border flex items-center justify-center text-xs font-bold text-muted-foreground shrink-0">
            {index + 1}
          </span>
          <FaultBadge tipo={item.tipo_fallo} />
          <span className="text-xs text-muted-foreground">
            {item.asignatura} · {item.tema}
          </span>
        </div>
        <button
          onClick={() => setExpanded((e) => !e)}
          className="text-muted-foreground hover:text-foreground transition-colors text-xs"
          aria-expanded={expanded}
        >
          {expanded ? "Colapsar" : "Expandir"}
        </button>
      </div>

      {/* Question */}
      <p className="text-sm font-semibold text-foreground leading-snug">
        {item.pregunta_original}
      </p>

      {expanded && (
        <>
          {/* Answer comparison */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
              <p className="text-[10px] font-bold uppercase tracking-wider text-rose-400 mb-1">
                Tu respuesta
              </p>
              <p className="text-xs text-foreground/80">{item.respuesta_alumno}</p>
            </div>
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1">
                Correcta
              </p>
              <p className="text-xs text-foreground/80">
                {item.respuesta_correcta}
              </p>
            </div>
          </div>

          {/* Root cause */}
          <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-amber-400 mb-0.5">
                Causa raíz
              </p>
              <p className="text-xs text-foreground/85 leading-relaxed">
                {item.causa_error}
              </p>
            </div>
          </div>

          {/* Source link – "Grounded in Source" principle */}
          <SourceLinkBox chunk_source={item.chunk_source} />
        </>
      )}
    </article>
  );
}

// ─── Autopsy Report ────────────────────────────────────────────────

function AutopsyReport({
  report,
  onReset,
}: {
  report: ExamAutopsyResponse;
  onReset: () => void;
}) {
  const faultCounts = report.error_items.reduce<Record<string, number>>(
    (acc, item) => {
      acc[item.tipo_fallo] = (acc[item.tipo_fallo] ?? 0) + 1;
      return acc;
    },
    {}
  );

  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* Report header */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
              <Microscope className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-display font-bold text-foreground">
                Autopsia: {report.nombre_examen}
              </h2>
              <p className="text-xs text-muted-foreground">
                {new Date(report.fecha_analisis).toLocaleDateString("es-ES", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}{" "}
                · {report.error_items.length} errores analizados
              </p>
            </div>
          </div>
          <button onClick={onReset} className="btn-ghost text-xs">
            <Trash2 className="w-3.5 h-3.5" />
            Nueva autopsia
          </button>
        </div>

        {/* Summary */}
        <p className="text-sm text-foreground/85 leading-relaxed border-l-2 border-primary/40 pl-4">
          {report.resumen}
        </p>

        {/* Fault breakdown */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { tipo: "confusion", label: "Confusión", color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20" },
            { tipo: "laguna", label: "Laguna", color: "text-rose-400", bg: "bg-rose-500/10 border-rose-500/20" },
            { tipo: "parcial", label: "Parcial", color: "text-primary", bg: "bg-primary/10 border-primary/20" },
          ].map(({ tipo, label, color, bg }) => (
            <div
              key={tipo}
              className={cn("rounded-xl border p-3 text-center", bg)}
            >
              <p className={cn("text-2xl font-display font-extrabold", color)}>
                {faultCounts[tipo] ?? 0}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">{label}</p>
            </div>
          ))}
        </div>

        {/* Start reinforcement session CTA */}
        <Link
          href={`/study?session=${report.sesion_refuerzo_id}`}
          id="btn-start-reinforcement"
          className="btn-primary w-full justify-center"
        >
          <Play className="w-4 h-4" fill="currentColor" />
          Iniciar sesión de refuerzo
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Error items list */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
          <Brain className="w-4 h-4 text-primary" />
          Análisis detallado de errores
        </h3>
        {report.error_items.map((item, idx) => (
          <ErrorItemCard key={item.item_id} item={item} index={idx} />
        ))}
      </div>
    </div>
  );
}

// ─── Upload Center ─────────────────────────────────────────────────

interface FileEntry {
  file: File;
  status: UploadStatus;
  error?: string;
}

interface UploadCenterProps {
  onAutopsyComplete: (report: ExamAutopsyResponse) => void;
}

function UploadCenter({ onAutopsyComplete }: UploadCenterProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [noteFiles, setNoteFiles] = useState<FileEntry[]>([]);
  const [examFile, setExamFile] = useState<File | null>(null);
  const [activeTab, setActiveTab] = useState<"notes" | "exam">("notes");

  const notesInputRef = useRef<HTMLInputElement>(null);
  const examInputRef = useRef<HTMLInputElement>(null);

  // ── Mutations ────────────────────────────────────────────────────
  const notesMutation = useMutation({
    mutationFn: ({ file, asignatura_id }: { file: File; asignatura_id: string }) =>
      documentsApi.uploadDocument(file, asignatura_id),
  });

  const autopsyMutation = useMutation({
    mutationFn: (file: File) => examApi.uploadExam(file),
    onSuccess: (data) => onAutopsyComplete(data),
  });

  // ── Drag handlers ────────────────────────────────────────────────
  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => setIsDragging(false), []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>, target: "notes" | "exam") => {
      e.preventDefault();
      setIsDragging(false);
      const files = Array.from(e.dataTransfer.files).filter(isAccepted);
      if (target === "notes") {
        setNoteFiles((prev) => [
          ...prev,
          ...files.map((f) => ({ file: f, status: "idle" as UploadStatus })),
        ]);
      } else if (files.length > 0) {
        setExamFile(files[0]);
      }
    },
    []
  );

  const handleNotesInput = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []).filter(isAccepted);
    setNoteFiles((prev) => [
      ...prev,
      ...files.map((f) => ({ file: f, status: "idle" as UploadStatus })),
    ]);
    e.target.value = "";
  }, []);

  const handleExamInput = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && isAccepted(file)) setExamFile(file);
    e.target.value = "";
  }, []);

  const removeNote = (idx: number) =>
    setNoteFiles((prev) => prev.filter((_, i) => i !== idx));

  // ── Upload actions ───────────────────────────────────────────────
  const uploadNotes = async () => {
    for (let i = 0; i < noteFiles.length; i++) {
      const entry = noteFiles[i];
      if (entry.status !== "idle") continue;
      setNoteFiles((prev) =>
        prev.map((e, idx) =>
          idx === i ? { ...e, status: "uploading" } : e
        )
      );
      try {
        await notesMutation.mutateAsync({
          file: entry.file,
          asignatura_id: "default",
        });
        setNoteFiles((prev) =>
          prev.map((e, idx) => (idx === i ? { ...e, status: "done" } : e))
        );
      } catch (err) {
        setNoteFiles((prev) =>
          prev.map((e, idx) =>
            idx === i
              ? {
                  ...e,
                  status: "error",
                  error:
                    err instanceof Error ? err.message : "Error desconocido",
                }
              : e
          )
        );
      }
    }
  };

  const uploadExam = () => {
    if (!examFile) return;
    autopsyMutation.mutate(examFile);
  };

  // ─── Render ──────────────────────────────────────────────────────
  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Page heading */}
      <div className="space-y-1">
        <h1 className="text-3xl font-display font-bold text-gradient">
          Centro de Carga
        </h1>
        <p className="text-sm text-muted-foreground">
          Sube tus apuntes para potenciar el tutor IA o analiza un examen
          suspendido.
        </p>
      </div>

      {/* OCR notice */}
      <div className="flex items-start gap-3 p-4 rounded-xl border border-primary/25 bg-primary/5 animate-fade-in-up">
        <ScanLine className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div className="text-sm">
          <span className="font-semibold text-foreground">
            OCR + Escritura manual soportados.
          </span>{" "}
          <span className="text-muted-foreground">
            El sistema usa{" "}
            <span className="font-medium text-foreground">
              Azure Document Intelligence
            </span>{" "}
            para extraer texto de PDFs, imágenes escaneadas y{" "}
            <span className="font-medium text-foreground">
              apuntes manuscritos
            </span>
            . ¡Sube tus cuadernos sin problema! ✍️
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border">
        {(["notes", "exam"] as const).map((tab) => (
          <button
            key={tab}
            id={`tab-${tab}`}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "px-5 py-3 text-sm font-semibold transition-all duration-200 border-b-2 -mb-px",
              activeTab === tab
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {tab === "notes" ? (
              <span className="flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                Apuntes y Materiales
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Microscope className="w-4 h-4" />
                Autopsia de Examen
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── Notes Tab ── */}
      {activeTab === "notes" && (
        <div className="space-y-5 animate-fade-in-up">
          {/* Drop zone */}
          <div
            className={cn("dropzone p-10 text-center cursor-pointer", isDragging && "dropzone-active")}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, "notes")}
            onClick={() => notesInputRef.current?.click()}
            role="button"
            tabIndex={0}
            id="notes-dropzone"
            onKeyDown={(e) => e.key === "Enter" && notesInputRef.current?.click()}
          >
            <input
              ref={notesInputRef}
              type="file"
              multiple
              accept={ACCEPTED.join(",")}
              className="hidden"
              onChange={handleNotesInput}
              id="notes-file-input"
            />
            <Upload
              className={cn(
                "w-10 h-10 mx-auto mb-3 transition-colors",
                isDragging ? "text-primary" : "text-muted-foreground/60"
              )}
            />
            <p className="font-semibold text-foreground">
              Arrastra tus apuntes aquí
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              PDF, DOCX, JPG, PNG · máx 25 MB por archivo
            </p>
            <p className="text-xs text-muted-foreground/70 mt-3 flex items-center justify-center gap-1">
              <ScanLine className="w-3 h-3" />
              Escritura manual y documentos escaneados compatibles
            </p>
          </div>

          {/* File list */}
          {noteFiles.length > 0 && (
            <div className="space-y-2">
              {noteFiles.map((entry, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 glass-card rounded-xl"
                >
                  {getFileIcon(entry.file.name)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {entry.file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(entry.file.size)}
                    </p>
                  </div>
                  {/* Status indicator */}
                  {entry.status === "idle" && (
                    <button
                      onClick={() => removeNote(idx)}
                      className="text-muted-foreground hover:text-rose-400 transition-colors"
                      aria-label="Eliminar"
                    >
                      <XCircle className="w-4 h-4" />
                    </button>
                  )}
                  {entry.status === "uploading" || entry.status === "processing" ? (
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                  ) : null}
                  {entry.status === "done" && (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                  {entry.status === "error" && (
                    <XCircle className="w-4 h-4 text-rose-400" title={entry.error} />
                  )}
                </div>
              ))}

              <button
                id="btn-upload-notes"
                className="btn-primary w-full justify-center mt-2"
                onClick={uploadNotes}
                disabled={
                  notesMutation.isPending ||
                  noteFiles.every((e) => e.status !== "idle")
                }
              >
                {notesMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Upload className="w-4 h-4" />
                )}
                Subir {noteFiles.filter((e) => e.status === "idle").length}{" "}
                archivo(s)
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── Exam Autopsy Tab ── */}
      {activeTab === "exam" && (
        <div className="space-y-5 animate-fade-in-up">
          <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 text-sm text-amber-400/90">
            <div className="flex items-center gap-2 font-semibold mb-1">
              <AlertTriangle className="w-4 h-4" />
              ¿Suspendiste un examen?
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Sube el PDF o foto del examen y el sistema identificará cada error,
              su causa raíz y qué parte de tus apuntes falló. Recibirás una
              sesión de refuerzo personalizada.
            </p>
          </div>

          {/* Drop zone */}
          <div
            className={cn("dropzone p-10 text-center cursor-pointer", isDragging && "dropzone-active")}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, "exam")}
            onClick={() => examInputRef.current?.click()}
            role="button"
            tabIndex={0}
            id="exam-dropzone"
            onKeyDown={(e) => e.key === "Enter" && examInputRef.current?.click()}
          >
            <input
              ref={examInputRef}
              type="file"
              accept={ACCEPTED.join(",")}
              className="hidden"
              onChange={handleExamInput}
              id="exam-file-input"
            />
            {examFile ? (
              <div className="flex items-center justify-center gap-3">
                {getFileIcon(examFile.name)}
                <div className="text-left">
                  <p className="font-semibold text-foreground">{examFile.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(examFile.size)} · Listo para analizar
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setExamFile(null);
                  }}
                  className="ml-2 text-muted-foreground hover:text-rose-400 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <>
                <Microscope
                  className={cn(
                    "w-10 h-10 mx-auto mb-3 transition-colors",
                    isDragging ? "text-primary" : "text-muted-foreground/60"
                  )}
                />
                <p className="font-semibold text-foreground">
                  Arrastra el examen aquí
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  PDF, JPG o PNG del examen · una sola hoja de examen
                </p>
              </>
            )}
          </div>

          {/* Upload + analyse */}
          {examFile && !autopsyMutation.isPending && !autopsyMutation.isSuccess && (
            <button
              id="btn-analyse-exam"
              className="btn-primary w-full justify-center"
              onClick={uploadExam}
            >
              <Brain className="w-4 h-4" />
              Analizar examen con IA
            </button>
          )}

          {autopsyMutation.isPending && (
            <div className="flex flex-col items-center gap-3 py-8 animate-fade-in-up">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <p className="text-sm font-semibold text-foreground">
                Analizando errores…
              </p>
              <p className="text-xs text-muted-foreground max-w-xs text-center">
                El tutor IA está procesando el examen y cruzando cada error con
                tus apuntes. Esto puede tardar unos segundos.
              </p>
              {/* Progress skeleton */}
              <div className="w-full max-w-sm space-y-2 mt-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="skeleton h-3 rounded-full" style={{ width: `${70 + i * 10}%` }} />
                ))}
              </div>
            </div>
          )}

          {autopsyMutation.isError && (
            <div className="flex items-center gap-2 text-sm text-rose-400 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <div>
                <p className="font-semibold">Error al analizar el examen</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {autopsyMutation.error instanceof Error
                    ? autopsyMutation.error.message
                    : "Error desconocido"}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Main Exported Component ───────────────────────────────────────

export default function ExamAutopsyReport() {
  const [report, setReport] = useState<ExamAutopsyResponse | null>(null);

  if (report) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10">
        <AutopsyReport report={report} onReset={() => setReport(null)} />
      </div>
    );
  }

  return <UploadCenter onAutopsyComplete={setReport} />;
}
