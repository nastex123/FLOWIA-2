'use client';

import React from 'react';

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
      <p className="font-serif text-xs font-bold tracking-wider text-slate-400 uppercase">
        {title}
      </p>
      <p
        className="font-serif text-3xl font-bold mt-2"
        style={{ color: colorHex }}
      >
        {value}
      </p>
      <div className="absolute -right-6 -bottom-6 w-20 h-20 rounded-full bg-crimson-900/10 pointer-events-none group-hover:bg-crimson-800/20 transition-all"></div>
    </div>
  );
}
