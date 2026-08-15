"use client";

import { useState, useRef } from "react";
import { UploadCloud, FileSpreadsheet, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { uploadDocument } from "@/lib/api";
import { formatBytes } from "@/lib/utils";

interface UploadDropzoneProps {
  onUploadSuccess: (docId: string) => void;
}

export default function UploadDropzone({ onUploadSuccess }: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    setSuccessMsg(null);
    const validExtensions = ["xlsx", "xls", "csv", "pdf"];
    const ext = file.name.split(".").pop()?.toLowerCase() || "";

    if (!validExtensions.includes(ext)) {
      setError(`Formato no soportado (.${ext}). Por favor sube un archivo Excel (.xlsx, .xls), CSV o PDF.`);
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setError("El archivo supera el límite máximo permitido de 25 MB.");
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await uploadDocument(selectedFile);
      setSuccessMsg(`Documento "${selectedFile.name}" subido correctamente. Procesando en segundo plano...`);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      onUploadSuccess(res.document_id);
    } catch (err: any) {
      setError(err.message || "Error al procesar la subida del documento");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Subir y Procesar Documento</h2>
          <p className="text-xs text-slate-400">
            Extracción determinista y clasificación local para hojas de cálculo y PDFs
          </p>
        </div>
        <div className="flex gap-1.5 text-[11px] font-medium text-slate-400">
          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700/60">.XLSX</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700/60">.CSV</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700/60">.PDF</span>
        </div>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragging
            ? "border-indigo-500 bg-indigo-500/10 scale-[0.99]"
            : "border-slate-700/80 bg-slate-950/50 hover:border-slate-600 hover:bg-slate-950/80"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,.xls,.csv,.pdf"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center gap-3">
          <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
            <UploadCloud className="w-7 h-7" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-200">
              Arrastra tu archivo aquí o <span className="text-indigo-400 underline decoration-indigo-400/40">haz clic para explorar</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">Soporta Excel, CSV y PDF hasta 25 MB</p>
          </div>
        </div>
      </div>

      {selectedFile && (
        <div className="mt-4 p-4 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {selectedFile.name.endsWith(".pdf") ? (
              <FileText className="w-8 h-8 text-rose-400" />
            ) : (
              <FileSpreadsheet className="w-8 h-8 text-emerald-400" />
            )}
            <div>
              <p className="text-sm font-medium text-slate-200 truncate max-w-sm">{selectedFile.name}</p>
              <p className="text-xs text-slate-400">{formatBytes(selectedFile.size)}</p>
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-colors"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                <UploadCloud className="w-4 h-4" />
                Procesar Ahora
              </>
            )}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}
    </div>
  );
}
