"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Database,
  FileSpreadsheet,
  Layers,
  Loader2,
  Plus,
  PlusCircle,
  Sparkles,
  Tag,
  Trash2,
  X,
} from "lucide-react";
import { createSchema, deleteSchema, listSchemas } from "@/lib/api";
import { useAuthGuard } from "@/lib/useAuthGuard";
import { DataType, FieldDefinition, SchemaCreate, SchemaResponse } from "@/types";

export default function SchemasPage() {
  useAuthGuard();

  const [schemas, setSchemas] = useState<SchemaResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal create state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newSchemaName, setNewSchemaName] = useState("");
  const [newSchemaDesc, setNewSchemaDesc] = useState("");
  const [newSchemaType, setNewSchemaType] = useState("custom");
  const [fields, setFields] = useState<FieldDefinition[]>([
    {
      name: "codigo",
      label: "Código / Referencia",
      data_type: "string",
      required: true,
      aliases: ["ref", "cod", "sku"],
    },
    {
      name: "descripcion",
      label: "Descripción del Item",
      data_type: "string",
      required: true,
      aliases: ["concepto", "producto", "articulo"],
    },
    {
      name: "importe",
      label: "Importe (€)",
      data_type: "number",
      required: false,
      aliases: ["precio", "total", "pvp"],
    },
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchSchemas = async () => {
    setIsLoading(true);
    try {
      const data = await listSchemas();
      setSchemas(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Error al cargar los esquemas de datos");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSchemas();
  }, []);

  const handleAddField = () => {
    setFields([
      ...fields,
      {
        name: `campo_${fields.length + 1}`,
        label: `Nuevo Campo ${fields.length + 1}`,
        data_type: "string",
        required: false,
        aliases: [],
      },
    ]);
  };

  const handleRemoveField = (index: number) => {
    if (fields.length <= 1) return;
    setFields(fields.filter((_, idx) => idx !== index));
  };

  const handleFieldChange = (index: number, key: keyof FieldDefinition, value: any) => {
    const updated = [...fields];
    if (key === "aliases" && typeof value === "string") {
      updated[index].aliases = value
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);
    } else {
      (updated[index] as any)[key] = value;
    }
    setFields(updated);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSchemaName.trim()) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const payload: SchemaCreate = {
        name: newSchemaName,
        description: newSchemaDesc,
        document_type: newSchemaType,
        fields: fields,
      };
      await createSchema(payload);
      setIsCreateOpen(false);
      setNewSchemaName("");
      setNewSchemaDesc("");
      await fetchSchemas();
    } catch (err: any) {
      setError(err.message || "Error al guardar el nuevo esquema");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteSchema = async (schemaId: string) => {
    if (!confirm("¿Estás seguro de que deseas eliminar este esquema personalizado?")) return;
    try {
      await deleteSchema(schemaId);
      await fetchSchemas();
    } catch (err: any) {
      alert(err.message || "Error al eliminar el esquema");
    }
  };

  return (
    <div className="space-y-8">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Database className="w-6 h-6 text-indigo-400" />
            Esquemas Canónicos de Datos
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Define la estructura canónica de datos de tu empresa para normalizar hojas de cálculo heterogéneas.
          </p>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          Crear Esquema Personalizado
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 2. Schemas Grid */}
      {isLoading ? (
        <div className="py-20 text-center bg-slate-900 border border-slate-800 rounded-3xl">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-300">Cargando esquemas disponibles...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {schemas.map((schema) => {
            const isPreset = schema.id.startsWith("preset-");
            return (
              <div
                key={schema.id}
                className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between hover:border-slate-700 transition-colors"
              >
                <div>
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-base">{schema.name}</span>
                        {isPreset ? (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            Plantilla Estándar
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            Personalizado
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{schema.description}</p>
                    </div>

                    {!isPreset && (
                      <button
                        onClick={() => handleDeleteSchema(schema.id)}
                        className="p-2 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                        title="Eliminar esquema"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-2">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Campos Definidos ({schema.fields.length})
                    </span>

                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                      {schema.fields.map((f) => (
                        <div
                          key={f.name}
                          className="flex items-center justify-between p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs"
                        >
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-indigo-400 font-semibold text-[11px]">
                              {f.name}
                            </span>
                            <span className="text-slate-300 font-medium">({f.label})</span>
                            {f.required && (
                              <span className="text-[10px] text-rose-400 font-bold">*</span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                              {f.data_type}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                  <span>Tipo: <strong className="text-slate-400 uppercase font-mono">{schema.document_type}</strong></span>
                  <span className="font-mono text-[10px]">ID: {schema.id}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 3. Modal Create Schema */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="p-6 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Crear Nuevo Esquema de Datos</h2>
                  <p className="text-xs text-slate-400">
                    Define las columnas destino y los alias de coincidencia difusa
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsCreateOpen(false)}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="p-6 overflow-y-auto flex-1 space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Nombre del Esquema *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Ej. Catálogo E-Commerce ERP"
                    value={newSchemaName}
                    onChange={(e) => setNewSchemaName(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Tipo de Documento
                  </label>
                  <select
                    value={newSchemaType}
                    onChange={(e) => setNewSchemaType(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="custom">Personalizado (Custom)</option>
                    <option value="inventory">Inventario / Stock</option>
                    <option value="invoice">Facturas / Recibos</option>
                    <option value="purchase_order">Órdenes de Compra</option>
                    <option value="payroll">Nóminas</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Descripción (Opcional)
                </label>
                <input
                  type="text"
                  placeholder="Propósito y especificaciones de este esquema"
                  value={newSchemaDesc}
                  onChange={(e) => setNewSchemaDesc(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Dynamic Fields Builder */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Campos del Esquema ({fields.length})
                  </span>
                  <button
                    type="button"
                    onClick={handleAddField}
                    className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-semibold"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    Añadir Campo
                  </button>
                </div>

                <div className="space-y-3">
                  {fields.map((f, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80 space-y-3"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-[10px] font-mono text-slate-500 font-bold">
                          Campo #{idx + 1}
                        </span>
                        {fields.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveField(idx)}
                            className="text-slate-500 hover:text-rose-400 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <label className="text-[10px] text-slate-400 block mb-1 font-medium">
                            Identificador (Key)
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="ej. precio_coste"
                            value={f.name}
                            onChange={(e) => handleFieldChange(idx, "name", e.target.value)}
                            className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] text-slate-400 block mb-1 font-medium">
                            Etiqueta Humana (Label)
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="ej. Precio de Coste (€)"
                            value={f.label}
                            onChange={(e) => handleFieldChange(idx, "label", e.target.value)}
                            className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] text-slate-400 block mb-1 font-medium">
                            Tipo de Dato
                          </label>
                          <select
                            value={f.data_type}
                            onChange={(e) =>
                              handleFieldChange(idx, "data_type", e.target.value as DataType)
                            }
                            className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                          >
                            <option value="string">Texto (String)</option>
                            <option value="number">Número (Number)</option>
                            <option value="date">Fecha (Date YYYY-MM-DD)</option>
                            <option value="boolean">Booleano (Boolean)</option>
                          </select>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 items-center">
                        <div className="sm:col-span-3">
                          <label className="text-[10px] text-slate-400 block mb-1 font-medium">
                            Alias para Auto-Matching (Separados por coma)
                          </label>
                          <input
                            type="text"
                            placeholder="ej. pvp, precio, coste_unitario, price"
                            value={f.aliases.join(", ")}
                            onChange={(e) => handleFieldChange(idx, "aliases", e.target.value)}
                            className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
                          />
                        </div>

                        <div className="flex items-center gap-2 pt-4">
                          <input
                            type="checkbox"
                            id={`req-${idx}`}
                            checked={f.required}
                            onChange={(e) => handleFieldChange(idx, "required", e.target.checked)}
                            className="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
                          />
                          <label htmlFor={`req-${idx}`} className="text-xs text-slate-300 cursor-pointer">
                            Obligatorio *
                          </label>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 border-t border-slate-800 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-indigo-600/20"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Guardando...
                    </>
                  ) : (
                    "Guardar Esquema"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
