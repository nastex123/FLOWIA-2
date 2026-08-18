'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Shield, Sparkles, LogIn } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('admin@flowmind.local');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.login(email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Error de autenticación');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoMode = () => {
    api.setDemoMode(true);
    router.push('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-2xl bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/40 p-8 shadow-2xl space-y-6">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-crimson-950/60 border border-crimson-600/40 flex items-center justify-center mx-auto text-crimson-400">
            <Shield className="w-6 h-6" />
          </div>
          <h1 className="font-serif text-2xl font-bold tracking-wider text-crimson-200">
            FLOWMIND AI
          </h1>
          <p className="text-xs text-slate-400">
            Cámara de Autenticación & Cripta Local
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-serif font-semibold text-slate-300 mb-1">
              Usuario / Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-obsidian-950/90 text-sm text-slate-200 px-4 py-2.5 rounded-lg border border-crimson-900/30 focus:border-crimson-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-serif font-semibold text-slate-300 mb-1">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-obsidian-950/90 text-sm text-slate-200 px-4 py-2.5 rounded-lg border border-crimson-900/30 focus:border-crimson-500 focus:outline-none"
              required
            />
          </div>

          {error && (
            <p className="text-xs text-rose-400 font-semibold">{error}</p>
          )}

          <div className="pt-2 space-y-3">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-gradient-to-r from-crimson-900 to-crimson-700 hover:from-crimson-800 hover:to-crimson-600 text-white font-serif font-bold text-xs shadow-md transition-all"
            >
              <LogIn className="w-4 h-4" />
              <span>{loading ? 'Conectando...' : 'Conectar al Santuario'}</span>
            </button>

            <button
              type="button"
              onClick={handleDemoMode}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/40 text-emerald-300 border border-emerald-600/40 font-serif font-bold text-xs shadow-sm transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>Ingresar en Modo Cripta Offline</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
