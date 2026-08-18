'use client';

import React, { useState } from 'react';
import { Upload, X, FileCheck, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface FileUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploaded: () => void;
}

export default function FileUploadModal({
  isOpen,
  onClose,
  onUploaded,
}: FileUploadModalProps) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      await api.uploadFile(file);
      onUploaded();
      onClose();
      setFile(null);
    } catch (err: any) {
      setError(err.message || 'Error al subir el comprobante.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="w-full max-w-lg rounded-2xl bg-obsidian-900 border border-crimson-900/40 p-6 shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-obsidian-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <h2 className="font-serif text-lg font-bold text-crimson-200">
          Subir Comprobante a la Cripta
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Archivos compatibles: PDF, Excel (XLSX, XLS), CSV e Imágenes (PNG, JPG).
        </p>

        {/* Dropzone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`mt-5 border-2 border-dashed rounded-xl p-8 text-center transition-all ${
            dragActive
              ? 'border-crimson-500 bg-crimson-950/20'
              : 'border-crimson-900/30 bg-obsidian-950/60'
          }`}
        >
          <Upload className="w-8 h-8 mx-auto text-crimson-400 mb-3" />
          <p className="text-sm font-medium text-slate-300">
            {file ? file.name : 'Arrastra tu archivo aquí o'}
          </p>
          <label className="inline-block mt-3 px-4 py-1.5 rounded-lg bg-obsidian-800 hover:bg-crimson-950/50 text-crimson-200 border border-crimson-900/40 text-xs font-semibold cursor-pointer transition-all">
            Examinar Archivo
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.jpeg"
              className="hidden"
            />
          </label>
        </div>

        {error && (
          <p className="text-xs text-rose-400 mt-3 font-semibold">{error}</p>
        )}

        {/* Actions */}
        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-obsidian-800 text-slate-300 hover:text-white text-xs font-semibold"
          >
            Cancelar
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-crimson-900 to-crimson-700 hover:from-crimson-800 hover:to-crimson-600 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>Iniciar Extracción</span>
          </button>
        </div>
      </div>
    </div>
  );
}
