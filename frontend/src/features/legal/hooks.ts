import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { legalApi, type DocumentListParams } from "../../lib/api";
import type { GenerateDocumentPayload, LegalDocument } from "../../lib/types";

export const legalKeys = {
  templates: ["templates"] as const,
  documents: (params: DocumentListParams) => ["documents", params] as const,
  document: (id: number) => ["document", id] as const,
};

export function useTemplates() {
  return useQuery({ queryKey: legalKeys.templates, queryFn: legalApi.templates });
}

export function useDocuments(params: DocumentListParams) {
  return useQuery({ queryKey: legalKeys.documents(params), queryFn: () => legalApi.documents(params) });
}

export function useDocument(id?: number) {
  return useQuery({ queryKey: legalKeys.document(id ?? 0), queryFn: () => legalApi.document(id!), enabled: Boolean(id) });
}

export function useGenerateDocument() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: GenerateDocumentPayload) => legalApi.generateDocument(payload),
    onSuccess: () => client.invalidateQueries({ queryKey: ["documents"] }),
  });
}

export function useUpdateDocument() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (document: LegalDocument) => legalApi.updateDocument(document),
    onSuccess: (document) => {
      client.invalidateQueries({ queryKey: ["documents"] });
      client.setQueryData(legalKeys.document(document.id), document);
    },
  });
}

export function useDeleteDocument() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => legalApi.deleteDocument(id),
    onSuccess: () => client.invalidateQueries({ queryKey: ["documents"] }),
  });
}

export function useExplainClause() {
  return useMutation({ mutationFn: ({ id, clause }: { id: number; clause: string }) => legalApi.explainClause(id, clause) });
}

export function useAnalyzeRisks() {
  return useMutation({ mutationFn: ({ id, content }: { id: number; content?: string }) => legalApi.analyzeRisks(id, content) });
}

export function useCompareDocuments() {
  return useMutation({
    mutationFn: ({ id, base, target }: { id: number; base: number; target: number }) => legalApi.compareDocuments(id, base, target),
  });
}
