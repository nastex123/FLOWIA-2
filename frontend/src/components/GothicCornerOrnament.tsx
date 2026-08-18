'use client';

import React from 'react';

interface GothicCornerOrnamentProps {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'all';
  className?: string;
  size?: number;
}

export default function GothicCornerOrnament({
  position = 'all',
  className = 'text-crimson-600/30 group-hover:text-crimson-500/60 transition-colors duration-500',
  size = 28,
}: GothicCornerOrnamentProps) {
  const renderCorner = (posClass: string, rotationClass: string) => (
    <div
      aria-hidden="true"
      className={`absolute ${posClass} pointer-events-none ${className} ${rotationClass}`}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="stroke-current stroke-[1.2]"
      >
        {/* Outer Corner Frame */}
        <path d="M2 30 L2 2 L30 2" />
        <path d="M6 26 L6 6 L26 6" strokeWidth="0.8" strokeDasharray="1.5 1.5" />

        {/* Cathedral Trefoil Arc */}
        <path d="M2 14 C10 14 14 10 14 2" strokeWidth="1" />
        <path d="M2 22 C16 22 22 16 22 2" strokeWidth="0.8" />

        {/* Gothic Fleur-de-lis / Rosette Accents */}
        <circle cx="10" cy="10" r="2.5" />
        <circle cx="10" cy="10" r="0.8" fill="currentColor" />
        <circle cx="18" cy="4" r="1.2" />
        <circle cx="4" cy="18" r="1.2" />
      </svg>
    </div>
  );

  if (position === 'top-left') return renderCorner('top-1.5 left-1.5', '');
  if (position === 'top-right') return renderCorner('top-1.5 right-1.5', 'scale-x-[-1]');
  if (position === 'bottom-left') return renderCorner('bottom-1.5 left-1.5', 'scale-y-[-1]');
  if (position === 'bottom-right') return renderCorner('bottom-1.5 right-1.5', 'scale-[-1]');

  return (
    <>
      {renderCorner('top-1.5 left-1.5', '')}
      {renderCorner('top-1.5 right-1.5', 'scale-x-[-1]')}
      {renderCorner('bottom-1.5 left-1.5', 'scale-y-[-1]')}
      {renderCorner('bottom-1.5 right-1.5', 'scale-[-1]')}
    </>
  );
}
