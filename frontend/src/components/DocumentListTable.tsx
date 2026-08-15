"use client";

import { useState } from "react";
import Link from "next/link";
import {
  FileSpreadsheet,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  RefreshCw,
  Search,
} from "lucide-react";
import { DocumentListItem } from "@/types";
import { formatBytes, formatDate } from "@/lib/utils";

interface DocumentListTableProps {
  documents: DocumentListItem[];
  isLoading: boolean;
  onRefresh: () => void;
}

export default function DocumentListTable({
  documents,
  isLoading,
  onRefresh,
}: DocumentListTableProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredDocs = documents.filter((d) =>
    d.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-lg font-semibold text-white">Documentos Procesados</h2>
          <p className="text-xs text-slate-400">
            Registro histórico de archivos y estado de extracción en base de datos local
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Buscar por nombre..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-48 sm:w-64"
            />
          </div>

          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Actualizar lista"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin text-indigo-400" : ""}`} />
          </button>
        </div>
      </div>

      {filteredDocs.length === 0 ? (
        <div className="text-center py-12 border border-slate-800/80 rounded-xl bg-slate-950/30">
          <FileSpreadsheet className="w-10 h-10 text-slate-600 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-300">No hay documentos registrados</p>
          <p className="text-xs text-slate-500 mt-1">
            {searchTerm ? "No se encontraron coincidencias para la búsqueda." : "Sube un archivo para comenzar la extracción."}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Documento</th>
                <th className="py-3 px-4">Tamaño</th>
                <th className="py-3 px-4">Fecha</th>
                <th className="py-3 px-4">Estado</th>
                <th className="py-3 px-4 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredDocs.map((doc) => {
                const isPdf = doc.filename.endsWith(".pdf");
                return (
                  <tr key={doc.document_id} className="hover:bg-slate-800/40 transition-colors group">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
                          {isPdf ? (
                            <FileText className="w-4 h-4 text-rose-400" />
                          ) : (
                            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                          )}
                        </div>
                        <div>
                          <span className="font-medium text-slate-200 block truncate max-w-xs sm:max-w-md">
                            {doc.filename}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">ID: {doc.document_id.slice(0, 8)}...</span>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">{formatBytes(doc.file_size_bytes)}</td>
                    <td className="py-3.5 px-4 text-slate-400">{formatDate(doc.created_at)}</td>
                    <td className="py-3.5 px-4">
                      {doc.status === "completed" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Completado
                        </span>
                      )}
                      {doc.status === "processing" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          Procesando
                        </span>
                      )}
                      {doc.status === "pending" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
                          <Clock className="w-3.5 h-3.5" />
                          En cola
                        </span>
                      )}
                      {doc.status === "failed" && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          Error
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/documents/${doc.document_id}`}
                        className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white font-medium transition-colors"
                      >
                        <span>Ver Datos</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
