"use client";

import { useEffect, useState } from "react";
import {
  FileSpreadsheet,
  CheckCircle2,
  Clock,
  Sparkles,
  Layers,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import UploadDropzone from "@/components/UploadDropzone";
import DocumentListTable from "@/components/DocumentListTable";
import { listDocuments } from "@/lib/api";
import { useAuthGuard } from "@/lib/useAuthGuard";
import { DocumentListItem } from "@/types";

export default function DashboardPage() {
  useAuthGuard();

  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDocs = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Error loading documents:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  // Poll if any document is currently in pending or processing
  useEffect(() => {
    const hasActiveJobs = documents.some(
      (d) => d.status === "pending" || d.status === "processing"
    );

    if (!hasActiveJobs) return;

    const interval = setInterval(() => {
      fetchDocs();
    }, 3000);

    return () => clearInterval(interval);
  }, [documents]);

  const completedCount = documents.filter((d) => d.status === "completed").length;
  const processingCount = documents.filter(
    (d) => d.status === "processing" || d.status === "pending"
  ).length;

  return (
    <div className="space-y-8">
      {/* 1. Hero / Header Summary */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Automatización Inteligente de Documentos
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Procesa hojas de cálculo (XLSX, CSV) y PDFs con extracción determinista y Machine Learning local.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
            Tenant: <strong>default-org</strong>
          </span>
        </div>
      </div>

      {/* 2. Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Archivos</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{documents.length}</p>
          <span className="text-[11px] text-slate-500 mt-1 block">Registrados en base local</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Completados</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{completedCount}</p>
          <span className="text-[11px] text-emerald-400/80 mt-1 block">Datos estructurados y validados</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">En Proceso</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">{processingCount}</p>
          <span className="text-[11px] text-amber-400/80 mt-1 block">Segundo plano (Zero Blocking)</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Privacidad</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <p className="text-2xl font-bold text-white mt-2">100%</p>
          <span className="text-[11px] text-emerald-400/80 mt-1 block">Cero fugas a nubes de IA</span>
        </div>
      </div>

      {/* 3. Upload Dropzone */}
      <UploadDropzone onUploadSuccess={() => fetchDocs()} />

      {/* 4. Documents Table */}
      <DocumentListTable
        documents={documents}
        isLoading={isLoading}
        onRefresh={() => fetchDocs()}
      />
    </div>
  );
}
