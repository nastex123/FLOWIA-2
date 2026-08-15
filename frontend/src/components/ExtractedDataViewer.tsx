"use client";

import { useState } from "react";
import {
  Brain,
  Download,
  FileCode,
  FileSpreadsheet,
  Layers,
  Search,
  Sparkles,
  Table as TableIcon,
  Tag,
} from "lucide-react";
import { DocumentDetail, ExtractedTable } from "@/types";
import { downloadCSV, downloadJSON } from "@/lib/utils";

interface ExtractedDataViewerProps {
  document: DocumentDetail;
}

export default function ExtractedDataViewer({ document }: ExtractedDataViewerProps) {
  const extraction = document.extraction;
  const tables = extraction?.tables || [];
  const fields = extraction?.fields || {};
  const fieldKeys = Object.keys(fields);

  const [activeTableIndex, setActiveTableIndex] = useState(0);
  const [tableSearch, setTableSearch] = useState("");

  if (!extraction) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center">
        <Layers className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-200">Sin datos de extracción disponibles</h3>
        <p className="text-xs text-slate-400 mt-1">
          {document.status === "processing"
            ? "El documento se está procesando actualmente. La página se actualizará automáticamente."
            : document.status === "failed"
            ? `Ocurrió un error: ${document.error_message || "Fallo desconocido"}`
            : "No se encontraron campos o tablas en este archivo."}
        </p>
      </div>
    );
  }

  const currentTable: ExtractedTable | undefined = tables[activeTableIndex];
  const filteredRecords = currentTable
    ? currentTable.records.filter((rec) =>
        Object.values(rec).some((val) =>
          String(val).toLowerCase().includes(tableSearch.toLowerCase())
        )
      )
    : [];

  return (
    <div className="space-y-6">
      {/* 1. Header with Classification & Export Actions */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 flex-shrink-0">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Tipo Detectado por ML
              </span>
              <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 capitalize">
                {extraction.document_type}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white mt-1">{document.filename}</h1>
            <div className="flex items-center gap-4 text-xs text-slate-400 mt-2">
              <span>Confianza: <strong>{(extraction.confidence * 100).toFixed(0)}%</strong></span>
              <span>•</span>
              <span>Tiempo: <strong>{extraction.processing_time_ms} ms</strong></span>
              <span>•</span>
              <span>Tablas: <strong>{tables.length}</strong></span>
              <span>•</span>
              <span>Campos clave: <strong>{fieldKeys.length}</strong></span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {currentTable && (
            <button
              onClick={() => downloadCSV(currentTable.records, `${document.filename}_${currentTable.sheet_or_page}`)}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-2 transition-colors border border-slate-700/60"
            >
              <Download className="w-3.5 h-3.5" />
              Descargar CSV
            </button>
          )}
          <button
            onClick={() => downloadJSON(extraction, `${document.filename}_extracted`)}
            className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-2 transition-colors shadow-lg shadow-indigo-600/20"
          >
            <FileCode className="w-3.5 h-3.5" />
            Descargar JSON
          </button>
        </div>
      </div>

      {/* 2. Key Extracted Fields Grid */}
      {fieldKeys.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Campos Clave Normalizados
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {fieldKeys.map((key) => {
              const field = fields[key];
              return (
                <div
                  key={key}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between text-slate-400 text-[11px] font-medium mb-1">
                    <span className="truncate capitalize">{key.replace(/_/g, " ")}</span>
                    <span className="text-[10px] text-emerald-400 font-mono">
                      {(field.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-base font-semibold text-slate-100 truncate">
                    {field.value !== null && field.value !== undefined ? String(field.value) : "—"}
                  </p>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 font-mono">
                    <span className="truncate">{field.extractor_type}</span>
                    {field.source_location && (
                      <span className="truncate max-w-[100px]">{field.source_location}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 3. Extracted Tabular Data Viewer */}
      {tables.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <TableIcon className="w-5 h-5 text-indigo-400" />
              <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
                Estructura Tabular ({tables.length} {tables.length === 1 ? "Hoja/Tabla" : "Hojas/Tablas"})
              </h2>
            </div>

            {/* Table Search */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filtrar celdas en tabla..."
                value={tableSearch}
                onChange={(e) => setTableSearch(e.target.value)}
                className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 w-full sm:w-64"
              />
            </div>
          </div>

          {/* Sheet / Table Tabs if multiple */}
          {tables.length > 1 && (
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
              {tables.map((t, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setActiveTableIndex(idx);
                    setTableSearch("");
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                    activeTableIndex === idx
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {t.sheet_or_page} ({t.rows_count} filas)
                </button>
              ))}
            </div>
          )}

          {/* Table Grid View */}
          {currentTable && (
            <div>
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>
                  Mostrando <strong>{filteredRecords.length}</strong> de {currentTable.rows_count} filas
                </span>
                <span>{currentTable.headers.length} columnas detectadas</span>
              </div>

              <div className="overflow-x-auto max-h-[500px] border border-slate-800 rounded-xl bg-slate-950/40">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="sticky top-0 bg-slate-900 border-b border-slate-800 z-10">
                    <tr>
                      <th className="py-2.5 px-3 text-slate-500 font-mono text-[10px] w-12 text-center">#</th>
                      {currentTable.headers.map((header, idx) => (
                        <th
                          key={idx}
                          className="py-2.5 px-3 font-semibold text-slate-300 whitespace-nowrap uppercase tracking-wider text-[11px]"
                        >
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredRecords.length === 0 ? (
                      <tr>
                        <td
                          colSpan={currentTable.headers.length + 1}
                          className="py-8 text-center text-slate-500 text-xs"
                        >
                          No hay filas que coincidan con la búsqueda.
                        </td>
                      </tr>
                    ) : (
                      filteredRecords.map((row, rIdx) => (
                        <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                          <td className="py-2 px-3 text-slate-500 font-mono text-[10px] text-center bg-slate-900/30">
                            {rIdx + 1}
                          </td>
                          {currentTable.headers.map((header, cIdx) => (
                            <td key={cIdx} className="py-2 px-3 text-slate-300 font-mono text-[11px] whitespace-nowrap">
                              {row[header] !== undefined && row[header] !== null
                                ? String(row[header])
                                : ""}
                            </td>
                          ))}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
