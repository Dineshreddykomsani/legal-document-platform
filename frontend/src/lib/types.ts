export type TemplateField = { name: string; label: string };

export type DocumentTemplate = {
  id: number;
  name: string;
  document_type: string;
  description: string;
  required_fields: TemplateField[];
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
  content: string;
  versions: DocumentVersion[];
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type GenerateDocumentPayload = {
  document_type: string;
  title: string;
  fields: Record<string, string>;
  save: boolean;
};

export type GeneratedDocumentResponse = {
  title: string;
  document_type: string;
  content: string;
  document: LegalDocument | null;
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
