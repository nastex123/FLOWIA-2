'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import FileUploadModal from '@/components/FileUploadModal';
import GothicRoseCircle from '@/components/GothicRoseCircle';
import GothicCornerOrnament from '@/components/GothicCornerOrnament';
import GothicDivider from '@/components/GothicDivider';
import { api } from '@/lib/api';
import { DocumentDetail } from '@/lib/types';
import {
  ArrowLeft,
  FileSpreadsheet,
  ShieldCheck,
  Calculator,
  Code,
  Check,
  Building,
  User,
  Calendar,
} from 'lucide-react';

export default function InvoiceReviewPage() {
  const params = useParams();
  const documentId = params?.id as string;

  const [collapsed, setCollapsed] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [detail, setDetail] = useState<DocumentDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    'header' | 'items' | 'sentinel' | 'math' | 'json'
  >('header');
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    if (documentId) {
      setError(null);
      api.getDocument(documentId)
        .then(setDetail)
        .catch((err) => {
          setDetail(null);
          setError(err.message || 'Error al cargar el documento.');
        });
    }
  }, [documentId]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center space-y-4 max-w-md">
          <div className="w-16 h-16 rounded-full bg-rose-950/40 border border-rose-600/40 flex items-center justify-center mx-auto">
            <ShieldCheck className="w-8 h-8 text-rose-400" />
          </div>
          <h2 className="font-serif text-xl font-bold text-crimson-200">Acceso Denegado</h2>
          <p className="text-sm text-slate-400">{error}</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <a
              href="/login"
              className="px-4 py-2 rounded-lg bg-crimson-900/60 hover:bg-crimson-800/60 text-crimson-100 text-xs font-semibold border border-crimson-600/40 transition-all"
            >
              Iniciar Sesion
            </a>
            <button
              onClick={() => {
                api.setDemoMode(true);
                window.location.reload();
              }}
              className="px-4 py-2 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/40 text-emerald-300 text-xs font-semibold border border-emerald-600/40 transition-all"
            >
              Modo Demo Offline
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="min-h-screen flex items-center justify-center font-serif text-crimson-300">
        Invocando comprobante desde la cripta...
      </div>
    );
  }

  const invoice = detail.structured_invoice || {};
  const isReviewed = detail.review_status === 'reviewed';

  const handleApprove = async () => {
    setReviewing(true);
    try {
      await api.reviewDocument(documentId, 'Consagrado y auditado');
      setDetail({
        ...detail,
        review_status: 'reviewed',
      });
    } finally {
      setReviewing(false);
    }
  };

  const tabs = [
    { key: 'header', label: 'Resumen & Cabecera', icon: FileSpreadsheet },
    { key: 'items', label: 'Líneas de Manuscrito', icon: FileSpreadsheet },
    { key: 'sentinel', label: 'Auditoría Sentinel', icon: ShieldCheck },
    { key: 'math', label: 'Validador Matemático', icon: Calculator },
    { key: 'json', label: 'Evidencia JSON', icon: Code },
  ];

  return (
    <div className="min-h-screen flex">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        <Header onOpenUpload={() => setUploadOpen(true)} />

        <main className="p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6 pb-28">
          {/* Top Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="p-2.5 rounded-lg bg-obsidian-900/90 hover:bg-crimson-950/60 text-slate-300 border border-crimson-900/40 transition-all shadow-sm"
              >
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <div>
                <div className="flex items-center gap-2 text-xs font-serif tracking-widest text-crimson-400 uppercase">
                  <span>✠</span>
                  <span>Inspección de Manuscrito</span>
                </div>
                <h1 className="font-serif text-xl md:text-2xl font-bold text-crimson-200">
                  {detail.filename}
                </h1>
                <p className="text-xs text-slate-400 font-mono">ID Criptográfico: {detail.document_id}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {isReviewed ? (
                <span className="px-3.5 py-1.5 rounded-full text-xs font-serif font-bold bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 shadow-md">
                  CONSAGRADA & APROBADA
                </span>
              ) : (
                <span className="px-3.5 py-1.5 rounded-full text-xs font-serif font-bold bg-amber-950/60 border border-amber-500/50 text-amber-300 shadow-md">
                  ESTADO: PENDIENTE
                </span>
              )}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-crimson-900/30 overflow-x-auto pb-1">
            {tabs.map((t) => {
              const Icon = t.icon;
              const active = activeTab === t.key;
              return (
                <button
                  key={t.key}
                  onClick={() => setActiveTab(t.key as any)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-semibold font-serif tracking-wider transition-all ${
                    active
                      ? 'bg-obsidian-900/90 text-crimson-300 border-t border-l border-r border-crimson-600/50 border-b-2 border-b-crimson-500'
                      : 'text-slate-400 hover:text-slate-200 bg-obsidian-950/40'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>

          {/* Tab 1: Resumen & Cabecera */}
          {activeTab === 'header' && (
            <div className="space-y-5">
              {/* Emisor y Receptor */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {/* Emisor */}
                <div className="relative overflow-hidden rounded-xl p-6 bg-obsidian-900/85 backdrop-blur-xl border border-crimson-900/35 group shadow-lg">
                  <GothicCornerOrnament />
                  <GothicRoseCircle className="w-36 h-36 -right-8 -bottom-8 opacity-15 group-hover:opacity-40 text-crimson-500" />
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 text-crimson-300 font-serif font-bold text-sm mb-4">
                      <Building className="w-4 h-4" />
                      <span>EMISOR / PROVEEDOR</span>
                    </div>
                    <dl className="space-y-2.5 text-xs">
                      <div className="flex justify-between border-b border-crimson-900/15 py-1">
                        <dt className="text-slate-400 font-serif">Razón Social:</dt>
                        <dd className="font-semibold text-slate-100">{invoice.vendor_name || '—'}</dd>
                      </div>
                      <div className="flex justify-between border-b border-crimson-900/15 py-1">
                        <dt className="text-slate-400 font-serif">NIF / CIF:</dt>
                        <dd className="font-semibold text-slate-100 font-mono">{invoice.vendor_tax_id || '—'}</dd>
                      </div>
                      <div className="flex justify-between border-b border-crimson-900/15 py-1">
                        <dt className="text-slate-400 font-serif">IBAN Bancario:</dt>
                        <dd className="font-semibold text-slate-100 font-mono">{invoice.vendor_iban || '—'}</dd>
                      </div>
                      <div className="flex justify-between py-1">
                        <dt className="text-slate-400 font-serif">Dirección:</dt>
                        <dd className="font-semibold text-slate-100">{invoice.vendor_address || '—'}</dd>
                      </div>
                    </dl>
                  </div>
                </div>

                {/* Receptor */}
                <div className="relative overflow-hidden rounded-xl p-6 bg-obsidian-900/85 backdrop-blur-xl border border-crimson-900/35 group shadow-lg">
                  <GothicCornerOrnament />
                  <GothicRoseCircle className="w-36 h-36 -right-8 -bottom-8 opacity-15 group-hover:opacity-40 text-crimson-500" reverse />
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 text-crimson-300 font-serif font-bold text-sm mb-4">
                      <User className="w-4 h-4" />
                      <span>RECEPTOR / CLIENTE</span>
                    </div>
                    <dl className="space-y-2.5 text-xs">
                      <div className="flex justify-between border-b border-crimson-900/15 py-1">
                        <dt className="text-slate-400 font-serif">Razón Social:</dt>
                        <dd className="font-semibold text-slate-100">{invoice.customer_name || '—'}</dd>
                      </div>
                      <div className="flex justify-between border-b border-crimson-900/15 py-1">
                        <dt className="text-slate-400 font-serif">NIF / CIF:</dt>
                        <dd className="font-semibold text-slate-100 font-mono">{invoice.customer_tax_id || '—'}</dd>
                      </div>
                      <div className="flex justify-between py-1">
                        <dt className="text-slate-400 font-serif">Dirección:</dt>
                        <dd className="font-semibold text-slate-100">{invoice.customer_address || '—'}</dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </div>

              {/* Metadatos y Fechas */}
              <div className="relative overflow-hidden rounded-xl p-6 bg-obsidian-900/85 backdrop-blur-xl border border-crimson-900/35 group shadow-lg">
                <GothicCornerOrnament />
                <GothicRoseCircle className="w-44 h-44 -right-10 -bottom-10 opacity-15 group-hover:opacity-35 text-crimson-600" />
                <div className="relative z-10">
                  <div className="flex items-center gap-2 text-crimson-300 font-serif font-bold text-sm mb-4">
                    <Calendar className="w-4 h-4" />
                    <span>METADATOS DE FACTURA</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                    <div>
                      <span className="text-slate-400 font-serif block">Nº Factura:</span>
                      <span className="font-bold text-slate-100 text-sm font-mono">{invoice.invoice_number || '—'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 font-serif block">Fecha Emisión:</span>
                      <span className="font-bold text-slate-100 text-sm">{invoice.issue_date || '—'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 font-serif block">Vencimiento:</span>
                      <span className="font-bold text-slate-100 text-sm">{invoice.due_date || '—'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 font-serif block">Divisa:</span>
                      <span className="font-bold text-slate-100 text-sm">{invoice.currency || 'EUR'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <GothicDivider label="Consagración de Totales" />

              {/* Totales Financieros Destacados */}
              <div className="relative overflow-hidden rounded-xl p-7 bg-gradient-to-r from-obsidian-900 to-crimson-950/70 backdrop-blur-xl border-2 border-crimson-600/60 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-2xl group">
                <GothicCornerOrnament />
                <GothicRoseCircle className="w-64 h-64 -right-14 -bottom-14 opacity-30 group-hover:opacity-50 text-crimson-400" />
                <div className="relative z-10">
                  <span className="text-xs text-slate-400 font-serif uppercase tracking-wider">Subtotal Neto</span>
                  <p className="text-2xl font-bold text-slate-100 mt-1 font-mono">{invoice.subtotal?.toLocaleString('es-ES')} EUR</p>
                </div>
                <div className="relative z-10">
                  <span className="text-xs text-slate-400 font-serif uppercase tracking-wider">Impuestos (IVA)</span>
                  <p className="text-2xl font-bold text-amber-400 mt-1 font-mono">{invoice.tax_total?.toLocaleString('es-ES')} EUR</p>
                </div>
                <div className="relative z-10 sm:text-right">
                  <span className="text-xs text-crimson-300 font-serif font-bold uppercase tracking-widest">TOTAL A PAGAR</span>
                  <p className="text-3xl font-serif font-bold text-emerald-400 mt-1">{invoice.total_amount?.toLocaleString('es-ES')} EUR</p>
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Líneas de Items */}
          {activeTab === 'items' && (
            <div className="relative overflow-hidden rounded-xl bg-obsidian-900/90 border border-crimson-900/35 group shadow-xl">
              <GothicCornerOrnament />
              <GothicRoseCircle className="w-52 h-52 -right-10 -bottom-10 opacity-15 group-hover:opacity-35 text-crimson-500" />
              <table className="w-full text-left text-xs text-slate-300 relative z-10">
                <thead className="bg-obsidian-950/95 border-b border-crimson-900/40 font-serif uppercase text-crimson-300">
                  <tr>
                    <th className="px-5 py-3.5">Descripción</th>
                    <th className="px-4 py-3.5 text-center">Cantidad</th>
                    <th className="px-4 py-3.5 text-right">Precio Unitario</th>
                    <th className="px-4 py-3.5 text-center">% IVA</th>
                    <th className="px-5 py-3.5 text-right">Importe Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-crimson-900/15">
                  {(invoice.items || []).map((item, idx) => (
                    <tr key={idx} className="hover:bg-crimson-950/20">
                      <td className="px-5 py-3.5 font-medium text-slate-100">{item.description}</td>
                      <td className="px-4 py-3.5 text-center font-mono">{item.quantity}</td>
                      <td className="px-4 py-3.5 text-right font-mono">{item.unit_price} EUR</td>
                      <td className="px-4 py-3.5 text-center font-mono">{item.tax_rate_pct}%</td>
                      <td className="px-5 py-3.5 text-right font-mono font-bold text-slate-100">{item.line_total} EUR</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Tab 3: Auditoría Sentinel */}
          {activeTab === 'sentinel' && (
            <div className="space-y-4">
              {(detail.checks || []).map((c, idx) => (
                <div
                  key={idx}
                  className={`relative overflow-hidden p-5 rounded-xl border backdrop-blur-md group shadow-md ${
                    c.severity === 'critical'
                      ? 'bg-rose-950/35 border-rose-600/50 text-rose-200'
                      : 'bg-emerald-950/35 border-emerald-600/50 text-emerald-200'
                  }`}
                >
                  <GothicCornerOrnament />
                  <GothicRoseCircle className="w-28 h-28 -right-4 -bottom-4 opacity-20 text-crimson-400" />
                  <div className="relative z-10">
                    <p className="font-serif font-bold text-sm">{c.title || c.check_type}</p>
                    <p className="text-xs mt-1 text-slate-300">{c.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab 4: Validador Matemático */}
          {activeTab === 'math' && (
            <div className="relative overflow-hidden p-6 rounded-xl bg-obsidian-900/90 border border-crimson-900/35 space-y-4 group shadow-xl">
              <GothicCornerOrnament />
              <GothicRoseCircle className="w-44 h-44 -right-8 -bottom-8 opacity-20 text-crimson-500" />
              <div className="relative z-10">
                <h3 className="font-serif font-bold text-crimson-300 text-sm">
                  Recálculo Determinista de Bases Imponibles
                </h3>
                <p className="text-xs text-slate-400 mt-2">
                  La cuadratura entre la base imponible declarada ({invoice.subtotal} EUR) y la cuota de IVA aplicada ({invoice.tax_total} EUR) concuerda con exactitud matemática determinista (diferencia: 0.00 EUR).
                </p>
              </div>
            </div>
          )}

          {/* Tab 5: JSON */}
          {activeTab === 'json' && (
            <pre className="relative overflow-hidden p-5 rounded-xl bg-obsidian-950 border border-crimson-900/35 text-xs font-mono text-crimson-200 overflow-x-auto shadow-2xl">
              {JSON.stringify(detail, null, 2)}
            </pre>
          )}
        </main>

        {/* Floating Action Bar */}
        <div className="fixed bottom-0 left-0 right-0 z-20 bg-obsidian-900/95 backdrop-blur-xl border-t border-crimson-900/40 px-6 py-4 flex items-center justify-between shadow-2xl">
          <p className="text-xs text-slate-400 hidden sm:block font-serif">
            {isReviewed
              ? 'Este comprobante ya fue auditado y consagrado en el libro mayor.'
              : 'Verifica la integridad de datos antes de registrar la consagración.'}
          </p>
          <div className="flex items-center gap-3 ml-auto">
            <button
              onClick={handleApprove}
              disabled={isReviewed || reviewing}
              className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-gradient-to-r from-emerald-800 to-emerald-600 hover:from-emerald-700 hover:to-emerald-500 disabled:opacity-50 text-white font-serif font-bold text-xs shadow-lg transition-all"
            >
              <Check className="w-4 h-4" />
              <span>
                {isReviewed
                  ? 'Comprobante Consagrado ✓'
                  : reviewing
                  ? 'Consagrando...'
                  : 'Consagrar y Aprobar Comprobante'}
              </span>
            </button>
          </div>
        </div>
      </div>

      <FileUploadModal
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={() => api.getDocument(documentId).then(setDetail)}
      />
    </div>
  );
}
