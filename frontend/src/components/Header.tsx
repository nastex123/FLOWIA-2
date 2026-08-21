'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Upload, LogIn, Database, CheckCircle2 } from 'lucide-react';
import { api } from '@/lib/api';
import { UserProfile } from '@/lib/types';

interface HeaderProps {
  onOpenUpload: () => void;
}

export default function Header({ onOpenUpload }: HeaderProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [selectedOrg, setSelectedOrg] = useState<string>('default-org');

  useEffect(() => {
    api.getProfile()
      .then((p) => {
        if (p && p.user && Array.isArray(p.organizations)) {
          setProfile(p);
        }
        setSelectedOrg(api.getOrganization());
      })
      .catch(() => {
        setProfile(null);
      });
  }, []);

  const handleOrgChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const orgId = e.target.value;
    setSelectedOrg(orgId);
    api.setOrganization(orgId);
    window.location.reload();
  };

  return (
    <header className="h-16 bg-obsidian-900/90 backdrop-blur-md border-b border-crimson-900/25 px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Brand & Cathedral Subtitle */}
      <div className="flex items-center gap-4">
        <span className="font-serif text-lg font-bold tracking-wider text-crimson-300">
          FLOWMIND AI
        </span>
        <span className="hidden md:inline text-xs text-slate-500 font-serif border-l border-crimson-900/30 pl-3">
          Catedral de Inteligencia Financiera & Auditoría Local
        </span>
      </div>

      {/* Actions & Sanctuary Pill */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenUpload}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-crimson-900 to-crimson-950 hover:from-crimson-800 hover:to-crimson-900 text-crimson-100 text-xs font-semibold border border-crimson-600/40 shadow-sm transition-all"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Subir Comprobante</span>
        </button>

        {profile && profile.organizations.length > 0 && (
          <select
            value={selectedOrg}
            onChange={handleOrgChange}
            className="bg-obsidian-800 text-xs text-slate-300 border border-crimson-900/30 rounded-lg px-2.5 py-1.5 focus:border-crimson-500 focus:outline-none"
          >
            {profile.organizations.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        )}

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Santuario Conectado</span>
        </div>

        <Link
          href="/login"
          className="p-2 rounded-lg bg-obsidian-800/80 hover:bg-crimson-950/40 text-slate-300 border border-crimson-900/20"
          title="Autenticación"
        >
          <LogIn className="w-4 h-4" />
        </Link>
      </div>
    </header>
  );
}
