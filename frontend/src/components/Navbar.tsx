"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Cpu, Database, FileSpreadsheet, Layers, ShieldCheck, Zap } from "lucide-react";
import { getHealth } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    getHealth()
      .then(() => setBackendHealthy(true))
      .catch(() => setBackendHealthy(false));
  }, []);

  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30 group-hover:bg-indigo-500 transition-colors">
              <Zap className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-lg tracking-tight text-white">
                  FlowMind <span className="text-indigo-400 font-normal">AI</span>
                </span>
                <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Local ML
                </span>
              </div>
              <span className="text-[11px] text-slate-400">Intelligent Document Automation</span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1 ml-4">
            <Link
              href="/"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/"
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              <span className="flex items-center gap-2">
                <Layers className="w-4 h-4" />
                Dashboard & Subida
              </span>
            </Link>
            <Link
              href="/schemas"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/schemas"
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              <span className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                Esquemas de Datos
              </span>
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
            <div
              className={`w-2 h-2 rounded-full ${
                backendHealthy === true
                  ? "bg-emerald-400 animate-pulse"
                  : backendHealthy === false
                  ? "bg-rose-400"
                  : "bg-amber-400"
              }`}
            />
            <span className="text-slate-300">
              {backendHealthy === true
                ? "Backend Conectado (Local)"
                : backendHealthy === false
                ? "Backend Desconectado"
                : "Conectando..."}
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 border border-slate-800 px-3 py-1.5 rounded-lg bg-slate-900">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Zero Cloud Leakage</span>
          </div>
        </div>
      </div>
    </header>
  );
}
