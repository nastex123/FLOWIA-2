'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import FileUploadModal from '@/components/FileUploadModal';
import GothicRoseCircle from '@/components/GothicRoseCircle';
import GothicCornerOrnament from '@/components/GothicCornerOrnament';
import GothicDivider from '@/components/GothicDivider';
import { Settings, Shield, FolderOpen, Key, Save, Check } from 'lucide-react';

export default function SettingsPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [saved, setSaved] = useState(false);

  const [hotFolderPath, setHotFolderPath] = useState('./data/hot_folder');
  const [minConfidence, setMinConfidence] = useState(85);
  const [duplicateThreshold, setDuplicateThreshold] = useState(90);
  const [storageBackend, setStorageBackend] = useState('local');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="min-h-screen flex">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        <Header onOpenUpload={() => setUploadOpen(true)} />

        <main className="p-6 md:p-8 max-w-5xl mx-auto w-full space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2 text-xs font-serif tracking-widest text-crimson-400 uppercase mb-1">
              <span>✠</span>
              <span>Cripta & Gobernanza Local</span>
            </div>
            <h1 className="font-serif text-2xl md:text-3xl font-bold text-crimson-200">
              Configuración de la Cripta
            </h1>
            <p className="text-xs md:text-sm text-slate-400 mt-1">
              Ajustes del motor antifraude Sentinel, agente Hot-Folder y políticas de almacenamiento 100% privado.
            </p>
          </div>

          <GothicDivider label="Políticas & Parámetros" />

          <form onSubmit={handleSave} className="space-y-5">
            {/* Card 1: Motor Sentinel */}
            <div className="relative overflow-hidden rounded-xl p-6 bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/35 group space-y-4 shadow-xl">
              <GothicCornerOrnament />
              <GothicRoseCircle className="w-48 h-48 -right-10 -bottom-10 opacity-20 group-hover:opacity-40 text-crimson-500" />
              <div className="flex items-center gap-2 text-crimson-300 font-serif font-bold text-sm">
                <Shield className="w-4 h-4" />
                <span>POLÍTICAS DE AUDITORÍA SENTINEL</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 relative z-10 text-xs">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">
                    Umbral Mínimo de Confianza en Extracción ({minConfidence}%)
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="99"
                    value={minConfidence}
                    onChange={(e) => setMinConfidence(Number(e.target.value))}
                    className="w-full accent-crimson-500 bg-obsidian-950 rounded-lg cursor-pointer"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">
                    Sensibilidad de Duplicidad Multidimensional ({duplicateThreshold}%)
                  </label>
                  <input
                    type="range"
                    min="60"
                    max="99"
                    value={duplicateThreshold}
                    onChange={(e) => setDuplicateThreshold(Number(e.target.value))}
                    className="w-full accent-crimson-500 bg-obsidian-950 rounded-lg cursor-pointer"
                  />
                </div>
              </div>
            </div>

            {/* Card 2: Hot-Folder */}
            <div className="relative overflow-hidden rounded-xl p-6 bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/35 group space-y-4 shadow-xl">
              <GothicCornerOrnament />
              <GothicRoseCircle className="w-48 h-48 -right-10 -bottom-10 opacity-20 group-hover:opacity-40 text-crimson-500" reverse />
              <div className="flex items-center gap-2 text-crimson-300 font-serif font-bold text-sm">
                <FolderOpen className="w-4 h-4" />
                <span>MONITOREO DE CARPETAS (HOT-FOLDER AGENT)</span>
              </div>
              <div className="relative z-10 space-y-3 text-xs">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">
                    Ruta de la Carpeta de Ingesta Automática
                  </label>
                  <input
                    type="text"
                    value={hotFolderPath}
                    onChange={(e) => setHotFolderPath(e.target.value)}
                    className="w-full bg-obsidian-950/90 text-sm text-slate-200 px-4 py-2 rounded-lg border border-crimson-900/30 focus:border-crimson-500 focus:outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">
                    Almacenamiento de Manuscritos
                  </label>
                  <select
                    value={storageBackend}
                    onChange={(e) => setStorageBackend(e.target.value)}
                    className="w-full bg-obsidian-950/90 text-sm text-slate-200 px-3 py-2 rounded-lg border border-crimson-900/30 focus:border-crimson-500 focus:outline-none"
                  >
                    <option value="local">Disco Local Cifrado (Local Storage)</option>
                    <option value="s3">Almacenamiento S3 / MinIO Local</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Card 3: Claves API */}
            <div className="relative overflow-hidden rounded-xl p-6 bg-obsidian-900/90 backdrop-blur-xl border border-crimson-900/35 group space-y-4 shadow-xl">
              <GothicCornerOrnament />
              <GothicRoseCircle className="w-48 h-48 -right-10 -bottom-10 opacity-20 group-hover:opacity-40 text-crimson-500" />
              <div className="flex items-center gap-2 text-crimson-300 font-serif font-bold text-sm">
                <Key className="w-4 h-4" />
                <span>CLAVES DE INTEGRACIÓN API (ORGANIZACIÓN ACTIVA)</span>
              </div>
              <div className="relative z-10 text-xs text-slate-400 space-y-2">
                <p>Clave API de Servicio: <span className="font-mono text-crimson-300 font-semibold">fm_live_sec_09827410293847</span></p>
                <p className="text-slate-500">Utiliza esta clave en cabeceras <span className="font-mono">X-API-Key</span> para ingestas desatendidas vía curl o scripts de backend.</p>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-gradient-to-r from-crimson-900 to-crimson-700 hover:from-crimson-800 hover:to-crimson-600 text-white font-serif font-bold text-xs shadow-lg transition-all"
              >
                {saved ? <Check className="w-4 h-4 text-emerald-300" /> : <Save className="w-4 h-4" />}
                <span>{saved ? 'Ajustes Guardados' : 'Guardar Configuración'}</span>
              </button>
            </div>
          </form>
        </main>
      </div>

      <FileUploadModal
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={() => {}}
      />
    </div>
  );
}
