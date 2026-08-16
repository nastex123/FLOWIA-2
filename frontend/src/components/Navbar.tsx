"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  Cpu,
  Database,
  Layers,
  LogOut,
  Settings,
  Zap,
} from "lucide-react";
import { getHealth, getMe } from "@/lib/api";
import { clearSession, getOrgId, setOrgId } from "@/lib/session";
import type { MeResponse } from "@/types";

export default function Navbar() {
  const pathname = usePathname();
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const [me, setMe] = useState<MeResponse | null>(null);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  const refreshMe = useCallback(() => {
    getMe()
      .then((data) => {
        setMe(data);
        setAuthenticated(true);
      })
      .catch(() => {
        setAuthenticated(false);
      });
  }, []);

  useEffect(() => {
    getHealth()
      .then(() => setBackendHealthy(true))
      .catch(() => setBackendHealthy(false));
    refreshMe();
  }, [refreshMe]);

  const handleOrgChange = (orgId: string) => {
    setOrgId(orgId);
    window.location.reload();
  };

  const handleLogout = () => {
    clearSession();
    window.location.href = "/login";
  };

  const activeOrgId = getOrgId() || me?.default_organization.id;

  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
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
                Dashboard
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
                Esquemas
              </span>
            </Link>
            <Link
              href="/settings"
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/settings"
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              <span className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Automatización
              </span>
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
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

          {authenticated === true && me ? (
            <>
              <select
                value={activeOrgId || ""}
                onChange={(e) => handleOrgChange(e.target.value)}
                title="Selector de organización"
                className="hidden sm:block text-xs bg-slate-800 border border-slate-700 rounded-lg px-2 py-1.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {me.organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name}
                  </option>
                ))}
              </select>

              <span className="hidden lg:inline-flex items-center text-xs text-slate-400 max-w-[160px] truncate">
                <Cpu className="w-3.5 h-3.5 mr-1.5 text-indigo-400" />
                {me.user.email}
                <span className="ml-1.5 px-1.5 py-0.5 rounded bg-slate-800 text-[10px] uppercase text-slate-400">
                  {me.user.role}
                </span>
              </span>

              <button
                onClick={handleLogout}
                title="Cerrar sesión"
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </>
          ) : authenticated === false ? (
            <Link
              href="/login"
              className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-500 transition-colors"
            >
              Iniciar Sesión
            </Link>
          ) : null}
        </div>
      </div>
    </header>
  );
}