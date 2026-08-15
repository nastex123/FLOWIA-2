"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Loader2, RefreshCw } from "lucide-react";
import ExtractedDataViewer from "@/components/ExtractedDataViewer";
import { getDocument } from "@/lib/api";
import { DocumentDetail } from "@/types";

export default function DocumentDetailPage() {
  const params = useParams();
  const documentId = params?.id as string;

  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDoc = async () => {
    if (!documentId) return;
    try {
      const data = await getDocument(documentId);
      setDocument(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Error al cargar los datos del documento");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDoc();
  }, [documentId]);

  // Poll if still processing
  useEffect(() => {
    if (document?.status === "pending" || document?.status === "processing") {
      const interval = setInterval(() => {
        fetchDoc();
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [document?.status]);

  return (
    <div className="space-y-6">
      {/* Back button */}
      <div>
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Volver al Dashboard</span>
        </Link>
      </div>

      {isLoading ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-16 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-300">Cargando datos del documento...</p>
        </div>
      ) : error ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center">
          <p className="text-sm text-rose-400 font-medium">{error}</p>
          <button
            onClick={fetchDoc}
            className="mt-4 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 inline-flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reintentar
          </button>
        </div>
      ) : document ? (
        <ExtractedDataViewer document={document} />
      ) : null}
    </div>
  );
}
