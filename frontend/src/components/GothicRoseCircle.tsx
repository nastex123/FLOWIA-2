'use client';

import React from 'react';

interface GothicRoseCircleProps {
  className?: string;
  size?: number;
  reverse?: boolean;
}

export default function GothicRoseCircle({
  className = 'w-36 h-36 -right-8 -bottom-8 opacity-20 group-hover:opacity-35 text-crimson-500',
  size = 180,
  reverse = false,
}: GothicRoseCircleProps) {
  return (
    <div
      className={`absolute pointer-events-none transition-opacity duration-500 ${
        reverse ? 'animate-[spin_50s_linear_infinite_reverse]' : 'animate-[spin_40s_linear_infinite]'
      } ${className}`}
    >
      <svg
        viewBox="0 0 100 100"
        width={size}
        height={size}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full stroke-current"
      >
        {/* Concentric Outer Rings */}
        <circle cx="50" cy="50" r="48" strokeWidth="1" />
        <circle cx="50" cy="50" r="45" strokeWidth="0.75" strokeDasharray="2 2" />
        <circle cx="50" cy="50" r="35" strokeWidth="0.85" />
        <circle cx="50" cy="50" r="20" strokeWidth="0.75" />
        <circle cx="50" cy="50" r="8" strokeWidth="1" />

        {/* 8-Pointed Octagram & Arches */}
        <path
          d="M50 2 L50 98 M2 50 L98 50 M16 16 L84 84 M16 84 L84 16"
          strokeWidth="0.5"
          strokeDasharray="1 3"
        />

        {/* 8 Gothic Lancet Petals */}
        <circle cx="50" cy="22" r="12" strokeWidth="0.75" />
        <circle cx="50" cy="78" r="12" strokeWidth="0.75" />
        <circle cx="22" cy="50" r="12" strokeWidth="0.75" />
        <circle cx="78" cy="50" r="12" strokeWidth="0.75" />
        <circle cx="30" cy="30" r="10" strokeWidth="0.6" />
        <circle cx="70" cy="70" r="10" strokeWidth="0.6" />
        <circle cx="30" cy="70" r="10" strokeWidth="0.6" />
        <circle cx="70" cy="30" r="10" strokeWidth="0.6" />

        {/* Inner Quadrafoil */}
        <path
          d="M50 38 Q56 44 50 50 Q44 44 50 38 Z"
          strokeWidth="0.6"
        />
        <path
          d="M50 62 Q56 56 50 50 Q44 56 50 62 Z"
          strokeWidth="0.6"
        />
        <path
          d="M38 50 Q44 56 50 50 Q44 44 38 50 Z"
          strokeWidth="0.6"
        />
        <path
          d="M62 50 Q56 56 50 50 Q56 44 62 50 Z"
          strokeWidth="0.6"
        />
      </svg>
    </div>
  );
}
