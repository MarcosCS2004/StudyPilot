// ──────────────────────────────────────────────
// StudyPilot – Centralised API Client
// Wraps fetch with base URL, auth headers and
// typed error handling for every endpoint.
// ──────────────────────────────────────────────
import type {
  ProfileProgressResponse,
  NextQuestionResponse,
  AnswerPayload,
  AnswerResponse,
  UploadResponse,
  ExamAutopsyResponse,
} from "@/types/api";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ─── HTTP Helper ───────────────────────────────
async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ─── Profile ───────────────────────────────────
export const profileApi = {
  getProgress: (): Promise<ProfileProgressResponse> =>
    apiFetch<ProfileProgressResponse>("/profile/progress"),
};

// ─── Study Session ─────────────────────────────
export const studyApi = {
  getNextQuestion: (asignatura_id?: string): Promise<NextQuestionResponse> =>
    apiFetch<NextQuestionResponse>(
      `/study/next-question${asignatura_id ? `?asignatura_id=${asignatura_id}` : ""}`
    ),

  submitAnswer: (payload: AnswerPayload): Promise<AnswerResponse> =>
    apiFetch<AnswerResponse>("/study/answer", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};

// ─── Documents ─────────────────────────────────
export const documentsApi = {
  uploadDocument: (file: File, asignatura_id: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("asignatura_id", asignatura_id);
    return apiFetch<UploadResponse>("/documents/upload", {
      method: "POST",
      body: formData,
      // Let browser set Content-Type multipart boundary
      headers: {},
    });
  },
};

// ─── Exam Autopsy ──────────────────────────────
export const examApi = {
  uploadExam: (file: File): Promise<ExamAutopsyResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch<ExamAutopsyResponse>("/exam-autopsy/upload", {
      method: "POST",
      body: formData,
      headers: {},
    });
  },
};
