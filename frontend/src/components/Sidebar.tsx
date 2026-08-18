'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  FileText,
  ClipboardCheck,
  Settings,
  Cpu,
  Menu,
  ChevronRight,
  Shield,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: 'Libro Mayor & Facturas', icon: FileText, glyph: 'I' },
    { href: '/review/doc_mock_001', label: 'Inspección de Factura', icon: ClipboardCheck, glyph: 'II' },
    { href: '/settings', label: 'Configuración de Cripta', icon: Settings, glyph: 'III' },
    { href: '/local', label: 'Extracción Local', icon: Cpu, glyph: 'IV' },
  ];

  return (
    <aside
      className={`fixed left-0 top-0 bottom-0 z-30 flex flex-col bg-obsidian-900/95 backdrop-blur-xl border-r border-crimson-900/30 transition-all duration-300 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-crimson-900/25">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-crimson-400" />
            <span className="font-serif text-sm font-bold tracking-wider text-crimson-300">
              FLOWMIND
            </span>
          </div>
        )}
        <button
          onClick={onToggle}
          aria-label="Colapsar menú lateral"
          className={`p-2 rounded-md bg-obsidian-800/80 hover:bg-crimson-950/60 text-crimson-300 border border-crimson-900/30 transition-colors ${
            collapsed ? 'mx-auto' : ''
          }`}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.label : undefined}
              className={`flex items-center gap-3 px-3.5 py-3 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-crimson-950/80 to-obsidian-800 text-crimson-200 border-l-4 border-crimson-600 font-semibold'
                  : 'text-slate-400 hover:text-crimson-200 hover:bg-obsidian-800/60 border-l-4 border-transparent'
              } ${collapsed ? 'justify-center px-0' : ''}`}
            >
              {collapsed ? (
                <span className="font-serif text-sm font-bold text-crimson-400">
                  [{item.glyph}]
                </span>
              ) : (
                <>
                  <Icon className="w-4 h-4 text-crimson-400 shrink-0" />
                  <span className="truncate">{item.label}</span>
                </>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-crimson-900/20 text-center">
        {!collapsed ? (
          <p className="font-serif text-xs text-crimson-900">
            FlowMind AI v0.2.0<br />
            <span className="text-slate-500 font-sans">100% Cripta Local</span>
          </p>
        ) : (
          <span className="font-serif text-xs text-crimson-800">FM</span>
        )}
      </div>
    </aside>
  );
}
