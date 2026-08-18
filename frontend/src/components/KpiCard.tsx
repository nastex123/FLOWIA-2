'use client';

import React from 'react';
import GothicRoseCircle from './GothicRoseCircle';
import GothicCornerOrnament from './GothicCornerOrnament';

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
      className={`relative overflow-hidden rounded-xl bg-obsidian-900/85 backdrop-blur-xl border border-crimson-900/35 p-5 shadow-lg hover:border-crimson-600/70 transition-all group ${borderColorClass}`}
    >
      <GothicCornerOrnament />
      <GothicRoseCircle className="w-36 h-36 -right-8 -bottom-8 opacity-20 group-hover:opacity-45 text-crimson-500" />

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
