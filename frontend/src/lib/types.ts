export interface CheckSummary {
  ok?: number;
  warning?: number;
  critical?: number;
}

export interface DocumentItem {
  document_id: string;
  filename: string;
  file_size_bytes?: number;
  status: string;
  review_status?: string;
  created_at: string;
  check_summary?: CheckSummary;
  error_message?: string | null;
}

export interface Organization {
  id: string;
  name: string;
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  tax_rate_pct: number;
  line_total: number;
}

export interface StructuredInvoice {
  vendor_name?: string;
  vendor_tax_id?: string;
  vendor_iban?: string;
  vendor_address?: string;
  customer_name?: string;
  customer_tax_id?: string;
  customer_address?: string;
  invoice_number?: string;
  issue_date?: string;
  due_date?: string;
  currency?: string;
  subtotal?: number;
  tax_total?: number;
  total_amount?: number;
  items?: InvoiceItem[];
}

export interface CheckResult {
  check_type: string;
  severity: 'ok' | 'warning' | 'critical';
  title: string;
  message: string;
}

export interface ExtractionInfo {
  document_type: string;
  confidence: number;
  fields: Record<string, any>;
  tables: any[];
  summary: string;
  processing_time_ms: number;
}

export interface DocumentDetail {
  document_id: string;
  organization_id: string;
  filename: string;
  file_size_bytes?: number;
  status: string;
  review_status: string;
  created_at: string;
  error_message?: string | null;
  extraction?: ExtractionInfo | null;
  structured_invoice?: StructuredInvoice;
  checks?: CheckResult[];
}

export interface UserProfile {
  user: {
    id: string;
    email: string;
    role: string;
    is_active: boolean;
    created_at: string;
  };
  default_organization: Organization;
  organizations: Organization[];
}
