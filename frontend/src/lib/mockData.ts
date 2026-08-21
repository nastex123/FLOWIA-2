import { DocumentDetail, DocumentItem, UserProfile } from './types';

export const MOCK_USER: UserProfile = {
  id: 'usr_01h7x',
  email: 'admin@flowmind.local',
  organizations: [
    { id: 'default-org', name: 'Santuario Principal SL' },
    { id: 'holding-org', name: 'Cripta & Holding Financiero SA' },
  ],
};

export const MOCK_DOCUMENTS: DocumentItem[] = [
  {
    document_id: 'doc_mock_001',
    filename: 'factura_suministros_2024.pdf',
    file_size: 145200,
    mime_type: 'application/pdf',
    status: 'COMPLETED',
    created_at: '2026-08-15T10:30:00Z',
    review_status: 'unreviewed',
    check_summary: { ok: 2, info: 1, warning: 1, critical: 1 },
  },
  {
    document_id: 'doc_mock_002',
    filename: 'factura_limpieza_industrial.xlsx',
    file_size: 34100,
    mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    status: 'COMPLETED',
    created_at: '2026-08-14T15:20:00Z',
    review_status: 'reviewed',
    check_summary: { ok: 3, info: 1, warning: 0, critical: 0 },
  },
  {
    document_id: 'doc_mock_003',
    filename: 'extracto_mensual_operaciones.csv',
    file_size: 18200,
    mime_type: 'text/csv',
    status: 'COMPLETED',
    created_at: '2026-08-13T09:12:00Z',
    review_status: 'unreviewed',
    check_summary: { ok: 4, info: 0, warning: 1, critical: 0 },
  },
];

export const MOCK_DOCUMENT_DETAILS: Record<string, DocumentDetail> = {
  doc_mock_001: {
    ...MOCK_DOCUMENTS[0],
    structured_invoice: {
      vendor_name: 'Suministros Industriales & Catedral SL',
      vendor_tax_id: 'B12345678',
      vendor_iban: 'ES9121000418450200051332',
      vendor_address: 'Calle Mayor 44, 28013 Madrid',
      customer_name: 'FlowMind Enterprise SA',
      customer_tax_id: 'A87654321',
      customer_address: 'Paseo de la Castellana 120, Madrid',
      invoice_number: 'INV-2024-0982',
      issue_date: '2024-06-15',
      due_date: '2024-07-15',
      currency: 'EUR',
      subtotal: 10392.0,
      tax_total: 2182.32,
      total_amount: 12574.32,
      items: [
        {
          description: 'Mantenimiento de Servidores y Criptas de Datos',
          quantity: 2,
          unit_price: 2450.0,
          tax_rate_pct: 21,
          line_total: 4900.0,
        },
        {
          description: 'Licencias de Procesamiento Determinista Offline',
          quantity: 4,
          unit_price: 850.5,
          tax_rate_pct: 21,
          line_total: 3402.0,
        },
        {
          description: 'Auditoría Forense de Grafos Relacionales',
          quantity: 10,
          unit_price: 45.0,
          tax_rate_pct: 21,
          line_total: 450.0,
        },
      ],
      tax_breakdown: [
        {
          tax_rate_pct: 21.0,
          taxable_base: 10392.0,
          tax_quota: 2182.32,
        },
      ],
    },
    checks: [
      {
        check_type: 'sentinel_iban_check',
        title: 'Alerta Sentinel: IBAN no registrado',
        message: 'El IBAN del proveedor no coincide con el registro histórico de transferencias previas.',
        severity: 'critical',
      },
      {
        check_type: 'math_tax_validation',
        title: 'Validación de Cuota IVA',
        message: 'La base imponible y el tipo del 21% concuerdan exactamente con la cuota de 2.182,32 EUR.',
        severity: 'ok',
      },
      {
        check_type: 'sentinel_duplicate_fingerprint',
        title: 'Inspección de Duplicados',
        message: 'No se detectaron colisiones de fingerprint con facturas previas en la organización.',
        severity: 'ok',
      },
    ],
  },
};
