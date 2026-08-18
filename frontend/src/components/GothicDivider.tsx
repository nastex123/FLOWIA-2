'use client';

import React from 'react';

interface GothicDividerProps {
  label?: string;
  className?: string;
}

export default function GothicDivider({ label, className = 'my-6' }: GothicDividerProps) {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Left Tapering Line */}
      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-crimson-900/60 to-crimson-600/70" />

      {/* Central Gothic Emblem */}
      <div className="px-4 flex items-center gap-2 text-crimson-400">
        <span className="text-xs font-serif tracking-widest text-crimson-500/80">✦</span>
        {label ? (
          <span className="font-serif text-xs font-bold uppercase tracking-widest text-crimson-300 px-2 py-0.5 rounded-full bg-obsidian-900/90 border border-crimson-900/40">
            {label}
          </span>
        ) : (
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.2"
            className="w-4 h-4 text-crimson-400"
          >
            {/* Gothic Rosette Cross */}
            <circle cx="12" cy="12" r="9" strokeDasharray="1.5 1.5" />
            <path d="M12 2 L12 22 M2 12 L22 12" />
            <circle cx="12" cy="12" r="3" fill="currentColor" fillOpacity="0.2" />
          </svg>
        )}
        <span className="text-xs font-serif tracking-widest text-crimson-500/80">✦</span>
      </div>

      {/* Right Tapering Line */}
      <div className="flex-1 h-px bg-gradient-to-l from-transparent via-crimson-900/60 to-crimson-600/70" />
    </div>
  );
}
