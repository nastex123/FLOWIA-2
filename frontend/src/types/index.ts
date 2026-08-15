export type DocumentType =
  | "invoice"
  | "purchase_order"
  | "payroll"
  | "inventory"
  | "receipt"
  | "contract"
  | "financial_report"
  | "unknown";

export type DocumentStatus = "pending" | "processing" | "completed" | "failed";

export interface ExtractedField {
  key: string;
  value: any;
  raw_value?: string;
  confidence: number;
  extractor_type: string;
  source_location?: string;
}

export interface ExtractedTable {
  sheet_or_page: string;
  headers: string[];
  rows_count: number;
  records: Record<string, any>[];
}

export interface ClassificationResult {
  document_type: DocumentType;
  confidence: number;
  classifier_type: string;
  matched_features: string[];
}

export interface ExtractionResult {
  document_id?: string;
  filename: string;
  classification: ClassificationResult;
  fields: Record<string, ExtractedField>;
  tables: ExtractedTable[];
  raw_text_summary?: string;
  processing_time_ms: number;
}

export interface DocumentListItem {
  document_id: string;
  filename: string;
  file_size_bytes: number;
  status: DocumentStatus;
  created_at: string;
}

export interface DocumentDetail {
  document_id: string;
  organization_id: string;
  filename: string;
  file_size_bytes: number;
  status: DocumentStatus;
  created_at: string;
  error_message?: string | null;
  extraction?: {
    document_type: string;
    confidence: number;
    fields: Record<string, ExtractedField>;
    tables: ExtractedTable[];
    summary?: string;
    processing_time_ms: number;
  } | null;
}
