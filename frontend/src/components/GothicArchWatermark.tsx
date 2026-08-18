'use client';

import React from 'react';

interface GothicArchWatermarkProps {
  className?: string;
}

export default function GothicArchWatermark({
  className = 'w-64 h-96 opacity-10 text-crimson-600 pointer-events-none',
}: GothicArchWatermarkProps) {
  return (
    <div className={`absolute ${className}`}>
      <svg
        viewBox="0 0 100 160"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full stroke-current stroke-[0.8]"
      >
        {/* Pointed Lancet Arch Outer Frame */}
        <path d="M10 160 L10 60 Q10 10 50 2 Q90 10 90 60 L90 160 Z" />
        <path d="M16 160 L16 62 Q16 16 50 10 Q84 16 84 62 L84 160" strokeDasharray="2 2" />

        {/* Inner Dual Lancets */}
        <path d="M22 160 L22 80 Q22 45 36 38 Q50 45 50 80 L50 160" strokeWidth="0.6" />
        <path d="M50 160 L50 80 Q50 45 64 38 Q78 45 78 80 L78 160" strokeWidth="0.6" />

        {/* Top Cathedral Rosette */}
        <circle cx="50" cy="26" r="10" strokeWidth="0.75" />
        <circle cx="50" cy="26" r="6" strokeDasharray="1.5 1.5" />
        <circle cx="50" cy="26" r="2" fill="currentColor" fillOpacity="0.3" />

        {/* Trefoil arches in Lancets */}
        <circle cx="36" cy="60" r="5" strokeWidth="0.5" />
        <circle cx="64" cy="60" r="5" strokeWidth="0.5" />

        {/* Bottom Horizontal Base */}
        <line x1="6" y1="158" x2="94" y2="158" strokeWidth="1.2" />
      </svg>
    </div>
  );
}
