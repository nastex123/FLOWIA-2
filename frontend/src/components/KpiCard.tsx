'use client';

import React from 'react';
import GothicRoseCircle from './GothicRoseCircle';

interface KpiCardProps {
  title: string;
  value: string | number;
  colorHex: string;
  borderColorClass: string;
}

export default function KpiCard({
  title,
  value,
  colorHex,
  borderColorClass,
}: KpiCardProps) {
  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-obsidian-900/80 backdrop-blur-xl border border-crimson-900/30 p-5 shadow-lg hover:border-crimson-600/60 transition-all group ${borderColorClass}`}
    >
      <GothicRoseCircle className="w-36 h-36 -right-8 -bottom-8 opacity-20 group-hover:opacity-40 text-crimson-500" />

      <p className="font-serif text-xs font-bold tracking-wider text-slate-400 uppercase relative z-10">
        {title}
      </p>
      <p
        className="font-serif text-3xl font-bold mt-2 relative z-10"
        style={{ color: colorHex }}
      >
        {value}
      </p>
    </div>
  );
}
