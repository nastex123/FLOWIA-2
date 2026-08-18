'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Search, Eye, AlertTriangle, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { DocumentItem } from '@/lib/types';

interface DocumentTableProps {
  documents: DocumentItem[];
  onRefresh: () => void;
}

export default function DocumentTable({ documents, onRefresh }: DocumentTableProps) {
  const [query, setQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'critical' | 'warning' | 'reviewed'>('all');

  const filtered = documents.filter((doc) => {
    const textMatch =
      !query ||
      doc.filename.toLowerCase().includes(query.toLowerCase()) ||
      doc.status.toLowerCase().includes(query.toLowerCase());

    if (!textMatch) return false;

    const criticalCount = doc.check_summary?.critical || 0;
    const warningCount = doc.check_summary?.warning || 0;
    const isReviewed = doc.review_status === 'reviewed';

    if (filterType === 'critical' && criticalCount === 0) return false;
    if (filterType === 'warning' && warningCount === 0) return false;
    if (filterType === 'reviewed' && !isReviewed) return false;

    return true;
  });

  const getSeverityBadge = (doc: DocumentItem) => {
    const summary = doc.check_summary;
    if (doc.review_status === 'reviewed') {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-950/60 border border-emerald-500/50 text-emerald-300">
          REVISADA
        </span>
      );
    }
    if (summary && summary.critical > 0) {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-950/60 border border-rose-500/50 text-rose-300">
          CRÍTICA
        </span>
      );
    }
    if (summary && summary.warning > 0) {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-950/60 border border-amber-500/50 text-amber-300">
          ADVERTENCIA
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-950/60 border border-purple-500/50 text-purple-300">
        VERIFICADO
      </span>
    );
  };

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-center justify-between p-3.5 rounded-xl bg-obsidian-900/80 backdrop-blur-md border border-crimson-900/30">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Buscar comprobante por nombre, emisor..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-obsidian-950/90 text-sm text-slate-200 pl-10 pr-4 py-2 rounded-lg border border-crimson-900/30 focus:border-crimson-500 focus:outline-none"
          />
        </div>

        {/* Filter Chips */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
          {[
            { key: 'all', label: 'Todos' },
            { key: 'critical', label: 'Críticos' },
            { key: 'warning', label: 'Advertencias' },
            { key: 'reviewed', label: 'Revisados' },
          ].map((chip) => (
            <button
              key={chip.key}
              onClick={() => setFilterType(chip.key as any)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                filterType === chip.key
                  ? 'bg-crimson-900/40 text-crimson-200 border border-crimson-600'
                  : 'bg-obsidian-800/80 text-slate-400 border border-crimson-900/20 hover:text-slate-200'
              }`}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table Panel */}
      <div className="rounded-xl overflow-hidden bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/30 shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-obsidian-950 border-b-2 border-crimson-900/40 font-serif text-xs uppercase tracking-wider text-crimson-300">
              <tr>
                <th className="px-5 py-3.5">Comprobante</th>
                <th className="px-4 py-3.5">Estado</th>
                <th className="px-4 py-3.5">Revisión</th>
                <th className="px-4 py-3.5">Severidad</th>
                <th className="px-3 py-3.5 text-center">OK</th>
                <th className="px-3 py-3.5 text-center">Warn</th>
                <th className="px-3 py-3.5 text-center">Crit</th>
                <th className="px-4 py-3.5">Fecha</th>
                <th className="px-4 py-3.5 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-crimson-900/15">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-10 text-slate-500 font-serif">
                    No se encontraron comprobantes registrados en la cripta.
                  </td>
                </tr>
              ) : (
                filtered.map((doc) => (
                  <tr
                    key={doc.document_id}
                    className="hover:bg-crimson-950/20 transition-colors"
                  >
                    <td className="px-5 py-4 font-medium text-slate-100 flex items-center gap-2">
                      <span className="font-serif text-xs text-crimson-400 font-bold">✠</span>
                      <span>{doc.filename}</span>
                    </td>
                    <td className="px-4 py-4 text-xs font-semibold text-slate-400">
                      {doc.status}
                    </td>
                    <td className="px-4 py-4 text-xs font-semibold uppercase text-slate-400">
                      {doc.review_status || 'PENDIENTE'}
                    </td>
                    <td className="px-4 py-4">{getSeverityBadge(doc)}</td>
                    <td className="px-3 py-4 text-center font-bold text-emerald-400">
                      {doc.check_summary?.ok || 0}
                    </td>
                    <td className="px-3 py-4 text-center font-bold text-amber-400">
                      {doc.check_summary?.warning || 0}
                    </td>
                    <td className="px-3 py-4 text-center font-bold text-rose-400">
                      {doc.check_summary?.critical || 0}
                    </td>
                    <td className="px-4 py-4 text-xs text-slate-400">
                      {doc.created_at.slice(0, 10)}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <Link
                        href={`/review/${doc.document_id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-obsidian-800 hover:bg-crimson-950/60 text-crimson-200 border border-crimson-900/30 text-xs font-semibold transition-all"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspeccionar</span>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
