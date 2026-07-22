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

const rawApiBaseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const normalizedApiBaseUrl = rawApiBaseUrl.replace(/\/$/, "");

export const API_BASE_URL = normalizedApiBaseUrl;
export const API_BASE = `${normalizedApiBaseUrl}/api/legal`;

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 45000,
});

function apiError(error: unknown) {
  if (!axios.isAxiosError(error)) return "Something went wrong.";
  const data = error.response?.data as { error?: { message?: unknown }; detail?: unknown } | undefined;
  const message = data?.error?.message ?? data?.detail;
  if (typeof message === "string") return message;
  if (message && typeof message === "object") {
    return Object.entries(message as Record<string, unknown>)
      .map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join(", ") : String(value)}`)
      .join("; ");
  }
  return error.message ?? "Request failed.";
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
    const { data } = await apiClient.get<PaginatedResponse<DocumentTemplate>>("templates/");
    return data;
  },
  async documents(params: DocumentListParams = {}) {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([, value]) => value !== undefined && value !== "" && value !== "all"),
    );
    const { data } = await apiClient.get<PaginatedResponse<LegalDocumentListItem>>("documents/", { params: cleanParams });
    return data;
  },
  async document(id: number) {
    const { data } = await apiClient.get<LegalDocument>(`documents/${id}/`);
    return data;
  },
  async updateDocument(document: LegalDocument) {
    const { data } = await apiClient.put<LegalDocument>(`documents/${document.id}/`, {
      title: document.title,
      document_type: document.document_type,
      content: document.content,
      status: document.status,
    });
    return data;
  },
  async deleteDocument(id: number) {
    await apiClient.delete(`documents/${id}/`);
  },
  async generateDocument(payload: GenerateDocumentPayload) {
    const hasLogo = Boolean(payload.company_logo);
    const body = hasLogo
      ? (() => {
          const form = new FormData();
          form.append("document_type", payload.document_type);
          if (payload.template_id) form.append("template_id", String(payload.template_id));
          form.append("title", payload.title);
          form.append("fields", JSON.stringify(payload.fields));
          form.append("branding", JSON.stringify(payload.branding ?? {}));
          form.append("save", String(payload.save));
          if (payload.company_logo) form.append("company_logo", payload.company_logo);
          return form;
        })()
      : payload;
    const { data } = await apiClient.post<GeneratedDocumentResponse>("documents/generate/", body);
    return data;
  },
  async explainClause(id: number, clause: string) {
    const { data } = await apiClient.post<ExplainClauseResponse>(`documents/${id}/explain-clause/`, { clause });
    return data;
  },
  async analyzeRisks(id: number, content?: string) {
    const { data } = await apiClient.post<RiskAnalysisResponse>(`documents/${id}/analyze-risks/`, { content });
    return data;
  },
  async compareDocuments(id: number, base_version_id: number, target_version_id: number) {
    const { data } = await apiClient.post<CompareResponse>(`documents/${id}/compare/`, {
      base_version_id,
      target_version_id,
    });
    return data;
  },
  pdfUrl(id: number) {
    return `${API_BASE}/documents/${id}/download-pdf/`;
  },
};
