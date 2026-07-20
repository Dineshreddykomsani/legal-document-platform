import axios from "axios";
import type {
  CompareResponse,
  DocumentStatus,
  DocumentTemplate,
  ExplainClauseResponse,
  GenerateDocumentPayload,
  GeneratedDocumentResponse,
  LegalDocument,
  LegalDocumentListItem,
  PaginatedResponse,
  RiskAnalysisResponse,
} from "./types";

export const API_BASE_URL = import.meta.env.VITE_API_URL;
export const API_BASE = `${API_BASE_URL.replace(/\/$/, "")}/api/legal`;

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 45000,
});

function apiError(error: unknown) {
  if (!axios.isAxiosError(error)) return "Something went wrong.";
  const data = error.response?.data as { error?: { message?: string }; detail?: string } | undefined;
  return data?.error?.message ?? data?.detail ?? error.message ?? "Request failed.";
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(new Error(apiError(error))),
);

export type DocumentListParams = {
  search?: string;
  status?: DocumentStatus | "all";
  document_type?: string;
  ordering?: string;
  page?: number;
};

export const legalApi = {
  async templates() {
    const { data } = await apiClient.get<PaginatedResponse<DocumentTemplate>>("/templates/");
    return data;
  },
  async documents(params: DocumentListParams = {}) {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([, value]) => value !== undefined && value !== "" && value !== "all"),
    );
    const { data } = await apiClient.get<PaginatedResponse<LegalDocumentListItem>>("/documents/", { params: cleanParams });
    return data;
  },
  async document(id: number) {
    const { data } = await apiClient.get<LegalDocument>(`/documents/${id}/`);
    return data;
  },
  async updateDocument(document: LegalDocument) {
    const { data } = await apiClient.put<LegalDocument>(`/documents/${document.id}/`, {
      title: document.title,
      document_type: document.document_type,
      content: document.content,
      status: document.status,
    });
    return data;
  },
  async deleteDocument(id: number) {
    await apiClient.delete(`/documents/${id}/`);
  },
  async generateDocument(payload: GenerateDocumentPayload) {
    const { data } = await apiClient.post<GeneratedDocumentResponse>("/documents/generate/", payload);
    return data;
  },
  async explainClause(id: number, clause: string) {
    const { data } = await apiClient.post<ExplainClauseResponse>(`/documents/${id}/explain-clause/`, { clause });
    return data;
  },
  async analyzeRisks(id: number, content?: string) {
    const { data } = await apiClient.post<RiskAnalysisResponse>(`/documents/${id}/analyze-risks/`, { content });
    return data;
  },
  async compareDocuments(id: number, base_version_id: number, target_version_id: number) {
    const { data } = await apiClient.post<CompareResponse>(`/documents/${id}/compare/`, {
      base_version_id,
      target_version_id,
    });
    return data;
  },
  pdfUrl(id: number) {
    return `${API_BASE}/documents/${id}/download-pdf/`;
  },
};
