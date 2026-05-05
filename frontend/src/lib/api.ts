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

import { useAuthStore } from "@/store/authStore";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ─── HTTP Helper ───────────────────────────────
async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const token = useAuthStore.getState().token;
  const headers = new Headers(init?.headers);
  
  // Only set JSON content type if it's not a FormData (which needs multipart boundary)
  if (!(init?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
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
      `/study/next-question?${asignatura_id ? `asignatura_id=${asignatura_id}&` : ""}t=${Date.now()}`
    ),

  submitAnswer: (payload: AnswerPayload): Promise<AnswerResponse> =>
    apiFetch<AnswerResponse>("/study/answer", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};

// ─── Chat ──────────────────────────────────────
export const chatApi = {
  sendMessage: (message: string, history: any[] = []): Promise<{ response: string; sources: string[] }> =>
    apiFetch<{ response: string; sources: string[] }>("/chat/", {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),
};

// ─── Documents ─────────────────────────────────
export const documentsApi = {
  getDocuments: (): Promise<any[]> =>
    apiFetch<any[]>("/documents"),

  uploadDocument: (file: File, asignatura_id: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("asignatura_id", asignatura_id);
    return apiFetch<UploadResponse>("/documents/upload", {
      method: "POST",
      body: formData,
    });
  },

  deleteDocument: (id: string): Promise<void> =>
    apiFetch<void>(`/documents/${id}`, { method: "DELETE" }),
};

// ─── Exam Autopsy ──────────────────────────────
export const examApi = {
  uploadExam: (file: File): Promise<ExamAutopsyResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch<ExamAutopsyResponse>("/autopsy/upload", {
      method: "POST",
      body: formData,
    });
  },

  getAutopsy: (id: string): Promise<ExamAutopsyResponse> =>
    apiFetch<ExamAutopsyResponse>(`/exam-autopsy/${id}`),

  getHistory: (): Promise<{ examenes: ExamAutopsyResponse[] }> =>
    apiFetch<{ examenes: ExamAutopsyResponse[] }>("/exam-autopsy/my-history"),

  clearHistory: (): Promise<void> =>
    apiFetch<void>("/exam-autopsy/my-history", { method: "DELETE" }),
};
