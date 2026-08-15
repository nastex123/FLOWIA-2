"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Database,
  Download,
  FileCode,
  FileSpreadsheet,
  Loader2,
  RefreshCw,
  Sparkles,
  Table as TableIcon,
  X,
} from "lucide-react";
import {
  autoMapColumns,
  listSchemas,
  normalizeDocument,
} from "@/lib/api";
import {
  AutoMapResponse,
  NormalizedDatasetResponse,
  SchemaResponse,
} from "@/types";
import { downloadCSV, downloadJSON } from "@/lib/utils";

interface SchemaMapperModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  filename: string;
  tableIndex: number;
  tableName: string;
  availableColumns: string[];
}

export default function SchemaMapperModal({
  isOpen,
  onClose,
  documentId,
  filename,
  tableIndex,
  tableName,
  availableColumns,
}: SchemaMapperModalProps) {
  const [schemas, setSchemas] = useState<SchemaResponse[]>([]);
  const [selectedSchemaId, setSelectedSchemaId] = useState<string>("");
  const [isLoadingSchemas, setIsLoadingSchemas] = useState(true);

  const [isAutoMapping, setIsAutoMapping] = useState(false);
  const [mappingState, setMappingState] = useState<Record<string, string>>({});
  const [autoMapData, setAutoMapData] = useState<AutoMapResponse | null>(null);

  const [isNormalizing, setIsNormalizing] = useState(false);
  const [normalizedResult, setNormalizedResult] =
    useState<NormalizedDatasetResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load available schemas on mount
  useEffect(() => {
    if (!isOpen) return;
    setIsLoadingSchemas(true);
    listSchemas()
      .then((data) => {
        setSchemas(data);
        if (data.length > 0) {
          setSelectedSchemaId(data[0].id);
        }
      })
      .catch((err) => console.error("Error loading schemas:", err))
      .finally(() => setIsLoadingSchemas(false));
  }, [isOpen]);

  // Trigger auto-mapping when a schema is selected
  useEffect(() => {
    if (!isOpen || !selectedSchemaId || !documentId) return;
    fetchAutoMapping(selectedSchemaId);
  }, [selectedSchemaId, isOpen]);

  const fetchAutoMapping = async (schemaId: string) => {
    setIsAutoMapping(true);
    setErrorMessage(null);
    setNormalizedResult(null);
    try {
      const res = await autoMapColumns(documentId, schemaId, tableIndex);
      setAutoMapData(res);

      const initialMap: Record<string, string> = {};
      for (const m of res.mappings) {
        if (m.suggested_source_column) {
          initialMap[m.target_field] = m.suggested_source_column;
        }
      }
      setMappingState(initialMap);
    } catch (err: any) {
      setErrorMessage(err.message || "Error al sugerir mapeos");
    } finally {
      setIsAutoMapping(false);
    }
  };

  const handleNormalize = async () => {
    if (!selectedSchemaId) return;
    setIsNormalizing(true);
    setErrorMessage(null);
    try {
      const res = await normalizeDocument(
        documentId,
        selectedSchemaId,
        mappingState,
        tableIndex
      );
      setNormalizedResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Error al normalizar los datos");
    } finally {
      setIsNormalizing(false);
    }
  };

  if (!isOpen) return null;

  const currentSchema = schemas.find((s) => s.id === selectedSchemaId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Mapeo & Normalización a Esquema Canónico
              </h2>
              <p className="text-xs text-slate-400">
                Archivo: <span className="text-slate-200 font-medium">{filename}</span> ({tableName})
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* 1. Schema Selector */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex-1">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1.5">
                Seleccionar Esquema Destino
              </label>
              {isLoadingSchemas ? (
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                  <span>Cargando esquemas disponibles...</span>
                </div>
              ) : (
                <select
                  value={selectedSchemaId}
                  onChange={(e) => setSelectedSchemaId(e.target.value)}
                  className="w-full sm:max-w-md px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-medium"
                >
                  {schemas.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.document_type}) — {s.fields.length} campos
                    </option>
                  ))}
                </select>
              )}
            </div>

            {currentSchema && (
              <div className="text-right hidden sm:block">
                <span className="text-xs text-slate-400 block">
                  {currentSchema.description || "Esquema empresarial para estandarización"}
                </span>
              </div>
            )}
          </div>

          {errorMessage && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* 2. Column Mapping Grid */}
          {!normalizedResult && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-sm font-semibold text-white">
                    Emparejamiento de Columnas (Fuzzy Matching)
                  </h3>
                </div>
                <button
                  onClick={() => fetchAutoMapping(selectedSchemaId)}
                  disabled={isAutoMapping}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isAutoMapping ? "animate-spin" : ""}`} />
                  <span>Re-calcular sugerencias</span>
                </button>
              </div>

              {isAutoMapping ? (
                <div className="py-12 text-center border border-slate-800 rounded-2xl bg-slate-950/30">
                  <Loader2 className="w-7 h-7 animate-spin text-indigo-400 mx-auto mb-2" />
                  <p className="text-xs text-slate-400">Analizando cabeceras y calculando afinidad difusa...</p>
                </div>
              ) : autoMapData ? (
                <div className="border border-slate-800 rounded-2xl overflow-hidden bg-slate-950/40">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 text-[10px] uppercase tracking-wider">
                        <th className="py-3 px-4">Campo del Esquema</th>
                        <th className="py-3 px-4">Tipo</th>
                        <th className="py-3 px-4 text-center"></th>
                        <th className="py-3 px-4">Columna en Archivo Subido</th>
                        <th className="py-3 px-4 text-right">Afinidad</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {autoMapData.mappings.map((m) => {
                        const currentVal = mappingState[m.target_field] || "";
                        return (
                          <tr key={m.target_field} className="hover:bg-slate-800/30 transition-colors">
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-1.5">
                                <span className="font-semibold text-slate-200">{m.target_label}</span>
                                {m.required && <span className="text-rose-400 text-xs font-bold">*</span>}
                              </div>
                              <span className="text-[10px] text-slate-500 font-mono">{m.target_field}</span>
                            </td>
                            <td className="py-3 px-4">
                              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                                {m.data_type}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-center text-slate-600">
                              <ArrowRight className="w-3.5 h-3.5 mx-auto" />
                            </td>
                            <td className="py-3 px-4">
                              <select
                                value={currentVal}
                                onChange={(e) =>
                                  setMappingState({
                                    ...mappingState,
                                    [m.target_field]: e.target.value,
                                  })
                                }
                                className={`w-full max-w-xs px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                                  currentVal
                                    ? "bg-slate-900 border-indigo-500/50 text-slate-100"
                                    : "bg-slate-950 border-slate-800 text-slate-500"
                                } border focus:outline-none focus:border-indigo-500`}
                              >
                                <option value="">-- No mapear (Ignorar) --</option>
                                {availableColumns.map((col) => (
                                  <option key={col} value={col}>
                                    {col}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="py-3 px-4 text-right">
                              {currentVal === m.suggested_source_column && m.confidence > 0 ? (
                                <span
                                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                    m.confidence >= 0.85
                                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                      : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                  }`}
                                >
                                  {(m.confidence * 100).toFixed(0)}% Match
                                </span>
                              ) : currentVal ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                                  Manual
                                </span>
                              ) : (
                                <span className="text-[10px] text-slate-600">—</span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </div>
          )}

          {/* 3. Normalized Dataset View */}
          {normalizedResult && (
            <div className="space-y-4 animate-in fade-in">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                  <div>
                    <h4 className="text-sm font-semibold text-emerald-200">
                      Normalización Completada con Éxito
                    </h4>
                    <p className="text-xs text-emerald-400/80">
                      {normalizedResult.total_records} registros estandarizados según el esquema "
                      {normalizedResult.schema_name}".
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      downloadCSV(
                        normalizedResult.records,
                        `${filename}_normalizado_${normalizedResult.schema_id}`
                      )
                    }
                    className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-2 transition-colors border border-slate-700"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Descargar CSV Normalizado
                  </button>
                  <button
                    onClick={() =>
                      downloadJSON(
                        normalizedResult.records,
                        `${filename}_normalizado_${normalizedResult.schema_id}`
                      )
                    }
                    className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-2 transition-colors"
                  >
                    <FileCode className="w-3.5 h-3.5" />
                    Descargar JSON
                  </button>
                </div>
              </div>

              {/* Validation errors warning if any */}
              {normalizedResult.validation_errors.length > 0 && (
                <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-2">
                  <div className="flex items-center gap-2 text-amber-300 text-xs font-semibold">
                    <AlertTriangle className="w-4 h-4" />
                    <span>
                      Se detectaron {normalizedResult.validation_errors.length} avisos de validación:
                    </span>
                  </div>
                  <ul className="text-[11px] text-amber-400/90 list-disc list-inside space-y-1 max-h-24 overflow-y-auto">
                    {normalizedResult.validation_errors.slice(0, 5).map((e, idx) => (
                      <li key={idx}>
                        Fila {e.row}: {e.error}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Normalized Data Table Preview */}
              <div className="border border-slate-800 rounded-2xl overflow-x-auto max-h-[350px] bg-slate-950/40">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="sticky top-0 bg-slate-900 border-b border-slate-800 z-10">
                    <tr>
                      <th className="py-2 px-3 text-slate-500 font-mono text-[10px] w-10 text-center">#</th>
                      {normalizedResult.headers.map((h) => (
                        <th key={h} className="py-2.5 px-3 font-semibold text-slate-200 uppercase tracking-wider text-[10px] whitespace-nowrap">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {normalizedResult.records.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-2 px-3 text-slate-500 font-mono text-[10px] text-center bg-slate-900/30">
                          {rIdx + 1}
                        </td>
                        {normalizedResult.headers.map((h) => (
                          <td key={h} className="py-2 px-3 text-slate-300 font-mono text-[11px] whitespace-nowrap">
                            {row[h] !== null && row[h] !== undefined ? String(row[h]) : "—"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex items-center justify-between">
          <div>
            {normalizedResult ? (
              <button
                onClick={() => setNormalizedResult(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
              >
                Volver a Ajustar Mapeo
              </button>
            ) : (
              <span className="text-xs text-slate-500">
                Los campos obligatorios marcados con * deben estar presentes.
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition-colors"
            >
              Cerrar
            </button>

            {!normalizedResult && (
              <button
                onClick={handleNormalize}
                disabled={isNormalizing || isAutoMapping}
                className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-colors"
              >
                {isNormalizing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Normalizando datos...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Normalizar Tabla
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
