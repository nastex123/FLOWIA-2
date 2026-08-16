export type DocumentType =
  | "invoice"
  | "purchase_order"
  | "payroll"
  | "inventory"
  | "receipt"
  | "contract"
  | "financial_report"
  | "custom"
  | "unknown";

export type DocumentStatus = "pending" | "processing" | "completed" | "failed";

export type DataType = "string" | "number" | "date" | "boolean";

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

export interface FieldDefinition {
  name: string;
  label: string;
  data_type: DataType;
  required: boolean;
  description?: string;
  aliases: string[];
}

export interface SchemaResponse {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  document_type: string;
  fields: FieldDefinition[];
  created_at: string;
  updated_at: string;
}

export interface SchemaCreate {
  name: string;
  description?: string;
  document_type: string;
  fields: FieldDefinition[];
}

export interface AutoMapSuggestion {
  target_field: string;
  target_label: string;
  data_type: DataType;
  required: boolean;
  suggested_source_column: string | null;
  confidence: number;
}

export interface AutoMapResponse {
  schema_id: string;
  schema_name: string;
  available_source_columns: string[];
  mappings: AutoMapSuggestion[];
}

export interface NormalizedDatasetResponse {
  schema_id: string;
  schema_name: string;
  total_records: number;
  headers: string[];
  records: Record<string, any>[];
  validation_errors: {
    row?: number;
    field?: string;
    raw_value?: any;
    error: string;
  }[];
}

// ==========================================
// Authentication, RBAC & API Keys
// ==========================================

export type UserRole = "admin" | "member" | "viewer";

export interface UserInfo {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface OrganizationInfo {
  id: string;
  name: string;
}

export interface MeResponse {
  user: UserInfo;
  default_organization: OrganizationInfo;
  organizations: OrganizationInfo[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: UserInfo;
}

export interface ApiKeyItem {
  id: string;
  organization_id: string;
  name: string;
  prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface ApiKeyCreated extends ApiKeyItem {
  key: string;
}

// ==========================================
// Automation Rules & Webhooks
// ==========================================

export type RuleEvent = "extraction_completed" | "normalization_completed";
export type RuleOperator =
  | "gt"
  | "lt"
  | "gte"
  | "lte"
  | "eq"
  | "neq"
  | "contains"
  | "is_empty"
  | "not_empty";

export interface AutomationRule {
  id: string;
  organization_id: string;
  name: string;
  description?: string | null;
  document_type?: string | null;
  event: RuleEvent;
  field: string;
  operator: RuleOperator;
  value?: any;
  webhook_ids: string[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AutomationRuleInput {
  name: string;
  description?: string | null;
  document_type?: string | null;
  event: RuleEvent;
  field: string;
  operator: RuleOperator;
  value?: any;
  webhook_ids: string[];
  enabled: boolean;
}

export interface WebhookConfig {
  id: string;
  organization_id: string;
  name: string;
  url: string;
  has_secret: boolean;
  headers: Record<string, string>;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WebhookConfigInput {
  name: string;
  url: string;
  secret?: string | null;
  headers?: Record<string, string>;
  active?: boolean;
}

export interface WebhookDelivery {
  id: string;
  organization_id: string;
  webhook_id?: string | null;
  rule_id?: string | null;
  document_id?: string | null;
  event: string;
  url: string;
  status: string;
  http_status?: number | null;
  error_message?: string | null;
  duration_ms: number;
  created_at: string;
}
