// ──────────────────────────────────────────────
// StudyPilot – API Type Definitions
// Mirrors the FastAPI response schemas exactly
// ──────────────────────────────────────────────

// ---- Profile & Progress ----

export interface TopicLevel {
  nombre_tema: string;
  nivel: number;        // 1–10
  pct_acierto: number;  // 0–100
}

export interface SubjectProgress {
  asignatura_id: string;
  nombre_asignatura: string;
  temas: TopicLevel[];
}

export interface ProfileProgressResponse {
  alumno_id: string;
  nombre: string;
  racha_dias: number;
  xp_total: number;
  asignaturas: SubjectProgress[];
}

// ---- Study Session ----

export type DifficultyLevel = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

export interface NextQuestionResponse {
  question_id: string;
  asignatura: string;
  tema: string;
  enunciado: string;
  opciones: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  nivel_dificultad: DifficultyLevel;
}

export interface AnswerPayload {
  question_id: string;
  respuesta: "A" | "B" | "C" | "D";
}

export interface AnswerResponse {
  correcto: boolean;
  respuesta_correcta: "A" | "B" | "C" | "D";
  explicacion: string;           // LLM-generated explanation
  nuevo_nivel_tema: number;      // Updated mastery level
  xp_ganado: number;
  siguiente_question_id?: string;
}

// ---- Document Upload ----

export type UploadStatus = "idle" | "uploading" | "processing" | "done" | "error";

export interface UploadedFile {
  id: string;
  nombre_archivo: string;
  tipo: "pdf" | "docx" | "jpg" | "png" | "unknown";
  status: UploadStatus;
  uploaded_at: string;
}

export interface UploadResponse {
  file_id: string;
  status: UploadStatus;
  mensaje: string;
}

// ---- Exam Autopsy ----

export type FaultType = "confusion" | "laguna" | "parcial";

export interface ErrorItem {
  item_id: string;
  pregunta_original: string;
  respuesta_alumno: string;
  respuesta_correcta: string;
  tipo_fallo: FaultType;
  causa_error: string;
  chunk_source: string;          // Relevant passage from the notes
  asignatura: string;
  tema: string;
}

export interface ExamAutopsyResponse {
  autopsy_id: string;
  nombre_examen: string;
  fecha_analisis: string;
  error_items: ErrorItem[];
  sesion_refuerzo_id: string;    // ID to launch a reinforcement session
  resumen: string;
}

// ---- Generic API helpers ----

export interface APIError {
  detail: string;
  status_code?: number;
}
