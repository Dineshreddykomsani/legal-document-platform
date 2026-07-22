export type TemplateField = { name: string; label: string };

export type DocumentTemplate = {
  id: number;
  name: string;
  document_type: string;
  description: string;
  required_fields: TemplateField[];
  preview_image?: string | null;
  theme: string;
  layout_id: string;
  header_style: string;
  footer_style: string;
  color_scheme: Record<string, string>;
  font: string;
};

export type DocumentVersion = {
  id: number;
  version_number: number;
  content: string;
  created_at: string;
};

export type DocumentStatus = "draft" | "generated";

export type LegalDocumentListItem = {
  id: number;
  title: string;
  document_type: string;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
  version_count: number;
};

export type LegalDocument = Omit<LegalDocumentListItem, "version_count"> & {
  template?: number | null;
  content: string;
  branding?: Record<string, string>;
  company_logo?: string | null;
  versions: DocumentVersion[];
};

export type CompanyBranding = {
  company_name?: string;
  address?: string;
  phone?: string;
  email?: string;
  website?: string;
  registration_number?: string;
  gst_number?: string;
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type GenerateDocumentPayload = {
  document_type: string;
  template_id?: number;
  title: string;
  fields: Record<string, string>;
  branding?: CompanyBranding;
  company_logo?: File | null;
  save: boolean;
};

export type GeneratedDocumentResponse = {
  title: string;
  document_type: string;
  content: string;
  document: LegalDocument | null;
  pdf_url?: string | null;
};

export type ExplainClauseResponse = {
  plain_english_explanation: string;
  purpose: string;
  business_impact: string;
};

export type RiskAnalysisResponse = {
  missing_clauses: string[];
  potential_legal_risks: string[];
  recommendations: string[];
  overall_risk_level: "low" | "medium" | "high";
};

export type CompareResponse = {
  base_version: number;
  target_version: number;
  added_content: string[];
  removed_content: string[];
  modified_content: string[];
  ai_summary: {
    summary: string;
    material_changes: string[];
    risk_notes: string[];
  };
};
