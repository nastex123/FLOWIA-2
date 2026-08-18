'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import FileUploadModal from '@/components/FileUploadModal';
import GothicRoseCircle from '@/components/GothicRoseCircle';
import { Cpu, Upload, FileText, CheckCircle2, Zap } from 'lucide-react';

export default function LocalExtractionPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);

  const [extractedData, setExtractedData] = useState<any>({
    filename: 'factura_suministros_2024.xlsx',
    document_type: 'INVOICE',
    confidence: 0.96,
    inference_time_ms: 142.5,
    fields: {
      invoice_number: { value: 'F-2024-0982', confidence: 0.98 },
      issue_date: { value: '2024-06-15', confidence: 0.99 },
      due_date: { value: '2024-07-15', confidence: 0.95 },
      vendor_name: { value: 'Suministros Industriales SL', confidence: 0.97 },
      vendor_tax_id: { value: 'B12345678', confidence: 1.0 },
      vendor_iban: { value: 'ES9121000418450200051332', confidence: 0.99 },
      total_amount: { value: '12.574,32 EUR', confidence: 1.0 },
    },
    records: [
      { col1: 'Mantenimiento Servidores', qty: 2, price: 2450.0, total: 4900.0 },
      { col1: 'Licencias Offline', qty: 4, price: 850.5, total: 3402.0 },
      { col1: 'Auditoría Forense', qty: 10, price: 45.0, total: 450.0 },
    ],
  });

  const handleSimulate = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setFile(f);
      setProcessing(true);
      setTimeout(() => {
        setExtractedData((prev: any) => ({
          ...prev,
          filename: f.name,
          inference_time_ms: (Math.random() * 80 + 110).toFixed(1),
        }));
        setProcessing(false);
      }, 1200);
    }
  };

  return (
    <div className="min-h-screen flex">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        <Header onOpenUpload={() => setUploadOpen(true)} />

        <main className="p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-crimson-200">
                Extracción en Cripta Local (Pure Libraries)
              </h1>
              <p className="text-xs md:text-sm text-slate-400 mt-1">
                Parsing determinista y clasificación ML offline mediante pandas, openpyxl, pdfplumber y scikit-learn.
              </p>
            </div>

            <label className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-crimson-900 to-crimson-700 hover:from-crimson-800 hover:to-crimson-600 text-white font-serif font-bold text-xs shadow-md cursor-pointer transition-all">
              <Upload className="w-4 h-4" />
              <span>{processing ? 'Extrayendo...' : 'Procesar Archivo Local'}</span>
              <input
                type="file"
                onChange={handleSimulate}
                className="hidden"
                accept=".xlsx,.xls,.csv,.pdf,.png,.jpg"
              />
            </label>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-obsidian-900/80 border border-crimson-900/30 flex items-center gap-3">
              <FileText className="w-5 h-5 text-crimson-400" />
              <div>
                <span className="text-xs text-slate-400 font-serif">Tipo Identificado</span>
                <p className="text-sm font-bold text-slate-100 uppercase font-serif">
                  {extractedData.document_type} ({(extractedData.confidence * 100).toFixed(0)}%)
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-obsidian-900/80 border border-crimson-900/30 flex items-center gap-3">
              <Zap className="w-5 h-5 text-amber-400" />
              <div>
                <span className="text-xs text-slate-400 font-serif">Tiempo de Inferencia</span>
                <p className="text-sm font-bold text-amber-300 font-mono">
                  {extractedData.inference_time_ms} ms (100% Local)
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-obsidian-900/80 border border-crimson-900/30 flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <div>
                <span className="text-xs text-slate-400 font-serif">Privacidad Garantizada</span>
                <p className="text-sm font-bold text-emerald-300">
                  Zero Cloud Data Leakage
                </p>
              </div>
            </div>
          </div>

          {/* 2-Column Splitter Workspace */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Campos Extraídos */}
            <div className="lg:col-span-5 relative overflow-hidden rounded-xl p-6 bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/30 group space-y-4">
              <GothicRoseCircle className="w-48 h-48 -right-10 -bottom-10 opacity-15 group-hover:opacity-35 text-crimson-500" />
              <h3 className="font-serif font-bold text-crimson-300 text-sm">
                Campos Clave Extraídos & Metadatos
              </h3>

              <div className="space-y-2.5 relative z-10 text-xs">
                {Object.entries(extractedData.fields).map(([key, item]: any) => (
                  <div
                    key={key}
                    className="p-2.5 rounded-lg bg-obsidian-950/80 border border-crimson-900/15 flex items-center justify-between"
                  >
                    <span className="text-slate-400 font-mono">{key}:</span>
                    <span className="font-semibold text-slate-100">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Tabular Grid */}
            <div className="lg:col-span-7 relative overflow-hidden rounded-xl bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/30 group">
              <GothicRoseCircle className="w-56 h-56 -right-12 -bottom-12 opacity-15 group-hover:opacity-30 text-crimson-500" reverse />
              <div className="p-5 border-b border-crimson-900/25">
                <h3 className="font-serif font-bold text-crimson-300 text-sm">
                  Grilla de Reconciliación Tabular
                </h3>
              </div>

              <div className="overflow-x-auto relative z-10">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-obsidian-950 font-serif uppercase text-crimson-300">
                    <tr>
                      <th className="px-5 py-3">Concepto</th>
                      <th className="px-4 py-3 text-center">Cantidad</th>
                      <th className="px-4 py-3 text-right">Precio Unitario</th>
                      <th className="px-5 py-3 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-crimson-900/15">
                    {extractedData.records.map((r: any, idx: number) => (
                      <tr key={idx} className="hover:bg-crimson-950/20">
                        <td className="px-5 py-3.5 font-medium text-slate-100">{r.col1}</td>
                        <td className="px-4 py-3.5 text-center font-mono">{r.qty}</td>
                        <td className="px-4 py-3.5 text-right font-mono">{r.price.toFixed(2)} EUR</td>
                        <td className="px-5 py-3.5 text-right font-mono font-bold text-slate-100">{r.total.toFixed(2)} EUR</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>

      <FileUploadModal
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={() => {}}
      />
    </div>
  );
}
