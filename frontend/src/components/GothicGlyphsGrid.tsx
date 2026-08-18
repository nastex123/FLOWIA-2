'use client';

import React from 'react';
import { ALL_GOTHIC_GLYPHS } from './GothicGlyphs';

interface GothicGlyphsGridProps {
  className?: string;
  columns?: number;
  interactive?: boolean;
}

export default function GothicGlyphsGrid({
  className = '',
  interactive = true,
}: GothicGlyphsGridProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-serif tracking-widest text-crimson-400 uppercase">
          <span>✠</span>
          <span>Catálogo de Sellos & Geometría Sagrada (24 Figuras de Catedral)</span>
        </div>
        <span className="text-xs text-slate-500 font-serif">Insignias Vectoriales Offline</span>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
        {ALL_GOTHIC_GLYPHS.map((glyph, idx) => {
          const GlyphComponent = glyph.Component;
          return (
            <div
              key={glyph.id}
              title={glyph.name}
              className={`relative overflow-hidden p-3.5 rounded-xl bg-obsidian-900/80 backdrop-blur-md border border-crimson-900/30 flex flex-col items-center justify-center text-center transition-all duration-300 group ${
                interactive
                  ? 'hover:border-crimson-500/70 hover:bg-crimson-950/30 hover:scale-105 shadow-md hover:shadow-crimson-950/50 cursor-pointer'
                  : ''
              }`}
            >
              <div className="w-10 h-10 flex items-center justify-center text-crimson-400 group-hover:text-crimson-300 transition-transform duration-500 group-hover:rotate-12">
                <GlyphComponent size={34} />
              </div>
              <span className="text-[10px] font-serif font-semibold text-slate-400 group-hover:text-slate-200 mt-2 truncate max-w-full">
                {glyph.name}
              </span>
              <span className="text-[9px] font-mono text-crimson-800 group-hover:text-crimson-400">
                #{String(idx + 1).padStart(2, '0')}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
