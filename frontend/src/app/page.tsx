'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import KpiCard from '@/components/KpiCard';
import DocumentTable from '@/components/DocumentTable';
import FileUploadModal from '@/components/FileUploadModal';
import GothicDivider from '@/components/GothicDivider';
import GothicArchWatermark from '@/components/GothicArchWatermark';
import GothicGlyphsGrid from '@/components/GothicGlyphsGrid';
import { api } from '@/lib/api';
import { DocumentItem } from '@/lib/types';
import { RefreshCw, Shield } from 'lucide-react';

export default function DashboardPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadOpen, setUploadOpen] = useState(false);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.listDocuments();
      setDocuments(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const total = documents.length;
  const critical = documents.filter(
    (d) => (d.check_summary?.critical || 0) > 0
  ).length;
  const warning = documents.filter(
    (d) => (d.check_summary?.warning || 0) > 0
  ).length;
  const reviewed = documents.filter(
    (d) => d.review_status === 'reviewed'
  ).length;

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        <Header onOpenUpload={() => setUploadOpen(true)} />

        <main className="p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6 relative">
          {/* Subtle Arch Watermark in Background */}
          <GothicArchWatermark className="w-80 h-[520px] -right-10 top-20 opacity-10 text-crimson-600 hidden xl:block" />

          {/* Header Title Section */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10">
            <div>
              <div className="flex items-center gap-2 text-xs font-serif tracking-widest text-crimson-400 uppercase mb-1">
                <span>✠</span>
                <span>Catedral de Inteligencia Financiera</span>
                <span>✠</span>
              </div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-crimson-200">
                Libro Mayor & Auditoría de Comprobantes
              </h1>
              <p className="text-xs md:text-sm text-slate-400 mt-1">
                Registro criptográfico, detección de anomalías y análisis determinista de facturas.
              </p>
            </div>
            <button
              onClick={fetchDocuments}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-obsidian-900/90 hover:bg-crimson-950/50 text-slate-300 border border-crimson-900/40 text-xs font-serif font-semibold shadow-sm transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Actualizar Registros</span>
            </button>
          </div>

          {/* 4 Gothic KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 relative z-10">
            <KpiCard
              title="Total Comprobantes"
              value={total}
              colorHex="#fda4af"
              borderColorClass="border-t-2 border-t-crimson-600"
            />
            <KpiCard
              title="Anomalías Críticas"
              value={critical}
              colorHex="#fb7185"
              borderColorClass="border-t-2 border-t-rose-600"
            />
            <KpiCard
              title="Advertencias Fiscales"
              value={warning}
              colorHex="#fde047"
              borderColorClass="border-t-2 border-t-amber-500"
            />
            <KpiCard
              title="Consagradas & Auditadas"
              value={reviewed}
              colorHex="#6ee7b7"
              borderColorClass="border-t-2 border-t-emerald-500"
            />
          </div>

          {/* Gothic Cathedral Divider */}
          <GothicDivider label="Registro Tabular & Auditoría" />

          {/* Document Table */}
          <div className="relative z-10">
            <DocumentTable documents={documents} onRefresh={fetchDocuments} />
          </div>

          {/* Gothic Cathedral Glyphs Grid (24 Figures) */}
          <GothicDivider label="Santuario de Sellos & Geometría Sagrada" />
          <div className="relative z-10">
            <GothicGlyphsGrid />
          </div>

          {/* Bottom Cathedral Footer Bar */}
          <div className="p-4 rounded-xl bg-obsidian-900/60 border border-crimson-900/20 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 font-serif">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-crimson-400" />
              <span>Protección Activa de Privacidad: 100% de la inferencia ejecutada en procesador local.</span>
            </div>
            <span className="text-crimson-800 font-bold mt-2 sm:mt-0">✦ Cero Filtración de Datos a la Nube ✦</span>
          </div>
        </main>
      </div>

      {/* File Upload Modal */}
      <FileUploadModal
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={fetchDocuments}
      />
    </div>
  );
}
