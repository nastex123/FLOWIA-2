'use client';

import React from 'react';

interface GlyphProps {
  className?: string;
  size?: number;
}

// 1. Cuadrifolio de Catedral
export const QuadrafoilGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" strokeDasharray="2 2" strokeWidth="0.8" />
    <circle cx="50" cy="28" r="20" />
    <circle cx="50" cy="72" r="20" />
    <circle cx="28" cy="50" r="20" />
    <circle cx="72" cy="50" r="20" />
    <circle cx="50" cy="50" r="8" fill="currentColor" fillOpacity="0.2" />
  </svg>
);

// 2. Trifolio Ojival
export const TrefoilGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="32" r="22" />
    <circle cx="32" cy="66" r="22" />
    <circle cx="68" cy="66" r="22" />
    <circle cx="50" cy="52" r="6" fill="currentColor" fillOpacity="0.25" />
    <path d="M50 4 L50 96 M4 50 L96 50" strokeWidth="0.6" strokeDasharray="2 3" />
  </svg>
);

// 3. Hexagrama Sacro de Catedral
export const HexagramGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" strokeDasharray="1.5 1.5" />
    <polygon points="50,6 88,72 12,72" />
    <polygon points="50,94 88,28 12,28" />
    <circle cx="50" cy="50" r="14" />
  </svg>
);

// 4. Octagrama del Santuario
export const OctagramGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" />
    <rect x="20" y="20" width="60" height="60" />
    <rect x="20" y="20" width="60" height="60" transform="rotate(45 50 50)" />
    <circle cx="50" cy="50" r="16" strokeDasharray="2 2" />
  </svg>
);

// 5. Cruz Templaria Paté
export const TemplarCrossGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M42 42 L10 16 L16 50 L10 84 L42 58 L50 90 L58 58 L90 84 L84 50 L90 16 L58 42 L50 10 Z" fill="currentColor" fillOpacity="0.15" />
    <circle cx="50" cy="50" r="45" strokeDasharray="2 3" strokeWidth="0.8" />
  </svg>
);

// 6. Rosetón Solar de 16 Rayos
export const SolarRosetteGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" />
    <circle cx="50" cy="50" r="32" strokeDasharray="2 2" />
    <circle cx="50" cy="50" r="14" fill="currentColor" fillOpacity="0.2" />
    {Array.from({ length: 16 }).map((_, i) => {
      const a = (Math.PI / 8) * i;
      return (
        <line
          key={i}
          x1={50 + Math.cos(a) * 14}
          y1={50 + Math.sin(a) * 14}
          x2={50 + Math.cos(a) * 46}
          y2={50 + Math.sin(a) * 46}
          strokeWidth="0.8"
        />
      );
    })}
  </svg>
);

// 7. Flor de Lis Gótica
export const FleurDeLisGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M50 10 C46 28 35 38 50 65 C65 38 54 28 50 10 Z" fill="currentColor" fillOpacity="0.2" />
    <path d="M50 65 C30 50 12 36 12 25 C12 18 20 18 28 26 C36 36 44 48 50 65 Z" />
    <path d="M50 65 C70 50 88 36 88 25 C88 18 80 18 72 26 C64 36 56 48 50 65 Z" />
    <rect x="25" y="62" width="50" height="8" rx="3" fill="currentColor" fillOpacity="0.3" />
    <path d="M40 70 L40 88 Q50 94 60 88 L60 70" />
  </svg>
);

// 8. Portal de Arco Ojival Flamígero
export const PointedArchPortalGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M15 90 L15 50 Q15 15 50 8 Q85 15 85 50 L85 90 Z" />
    <path d="M25 90 L25 54 Q25 24 50 18 Q75 24 75 54 L75 90" strokeDasharray="2 2" />
    <circle cx="50" cy="35" r="10" />
    <line x1="50" y1="45" x2="50" y2="90" strokeWidth="0.8" />
  </svg>
);

// 9. Arco Conopial / Ogee
export const OgeeArchGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M15 90 L15 55 Q15 35 32 30 Q50 25 50 6 Q50 25 68 30 Q85 35 85 55 L85 90 Z" />
    <circle cx="50" cy="48" r="14" strokeDasharray="1.5 1.5" />
    <circle cx="50" cy="48" r="4" fill="currentColor" />
  </svg>
);

// 10. Bóveda de Crucería / Rib Grid
export const VaultRibGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <rect x="10" y="10" width="80" height="80" />
    <line x1="10" y1="10" x2="90" y2="90" />
    <line x1="90" y1="10" x2="10" y2="90" />
    <circle cx="50" cy="50" r="28" strokeDasharray="2 2" />
    <circle cx="50" cy="50" r="10" fill="currentColor" fillOpacity="0.2" />
  </svg>
);

// 11. Óculo Gótico Central
export const OculiGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" />
    <circle cx="50" cy="50" r="38" />
    <circle cx="50" cy="50" r="24" strokeDasharray="2 2" />
    <circle cx="50" cy="30" r="8" />
    <circle cx="50" cy="70" r="8" />
    <circle cx="30" cy="50" r="8" />
    <circle cx="70" cy="50" r="8" />
    <circle cx="50" cy="50" r="5" fill="currentColor" />
  </svg>
);

// 12. Sello Alquímico de Saturno
export const AlchemicalSaturnGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" strokeDasharray="2 2" />
    <line x1="50" y1="12" x2="50" y2="88" />
    <line x1="30" y1="26" x2="70" y2="26" />
    <path d="M50 50 Q75 50 75 72 Q75 88 50 88 Q35 88 35 76" />
  </svg>
);

// 13. Compás del Maestro Cantero
export const MasonCompassGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="18" r="8" fill="currentColor" fillOpacity="0.2" />
    <line x1="50" y1="26" x2="16" y2="88" strokeWidth="1.5" />
    <line x1="50" y1="26" x2="84" y2="88" strokeWidth="1.5" />
    <path d="M28 68 Q50 80 72 68" strokeDasharray="2 2" />
    <circle cx="50" cy="74" r="3" fill="currentColor" />
  </svg>
);

// 14. Dodecagrama de 12 Lancetas
export const DodecagramGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" />
    <circle cx="50" cy="50" r="28" strokeDasharray="2 2" />
    {Array.from({ length: 12 }).map((_, i) => {
      const a = ((Math.PI * 2) / 12) * i;
      const px = 50 + Math.cos(a) * 36;
      const py = 50 + Math.sin(a) * 36;
      return <circle key={i} cx={px} cy={py} r="8" strokeWidth="0.7" />;
    })}
    <circle cx="50" cy="50" r="6" fill="currentColor" fillOpacity="0.3" />
  </svg>
);

// 15. Pináculo y Aguja Gótica
export const PinnacleSpireGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M50 4 L30 75 L30 96 L70 96 L70 75 Z" />
    <line x1="50" y1="4" x2="50" y2="96" strokeWidth="0.8" strokeDasharray="2 2" />
    <circle cx="50" cy="40" r="6" />
    <path d="M40 75 L60 75" />
    <circle cx="50" cy="4" r="2" fill="currentColor" />
  </svg>
);

// 16. Glifo de Gárgola Guardiana
export const GargoyleSigilGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M18 20 Q50 40 82 20 Q70 60 50 86 Q30 60 18 20 Z" fill="currentColor" fillOpacity="0.1" />
    <circle cx="36" cy="42" r="5" fill="currentColor" />
    <circle cx="64" cy="42" r="5" fill="currentColor" />
    <path d="M40 64 Q50 72 60 64" />
  </svg>
);

// 17. Hoja de Acanto Gótica
export const AcanthusLeafGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M50 94 Q50 50 16 38 Q32 30 50 45 Q50 20 50 6 Q50 20 50 45 Q68 30 84 38 Q50 50 50 94 Z" fill="currentColor" fillOpacity="0.15" />
  </svg>
);

// 18. Escuadra y Compás Cantero
export const MasonicSquareGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    {/* Compass */}
    <path d="M50 14 L22 84 M50 14 L78 84" strokeWidth="1.5" />
    {/* Square */}
    <path d="M18 42 L50 78 L82 42" strokeWidth="2" />
    <circle cx="50" cy="48" r="6" fill="currentColor" fillOpacity="0.3" />
  </svg>
);

// 19. Arbotante y Contrafuerte
export const ButtressArchGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M12 90 L12 25 Q12 10 30 10 L45 10" />
    <path d="M45 10 Q75 18 88 55 L88 90" strokeWidth="1.5" />
    <path d="M45 28 Q65 35 74 65 L74 90" strokeDasharray="2 2" />
    <circle cx="28" cy="48" r="10" />
  </svg>
);

// 20. Sello Criptográfico Medieval
export const CryptSealGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" />
    <circle cx="50" cy="50" r="42" strokeDasharray="1.5 2" />
    <circle cx="50" cy="50" r="30" />
    <path d="M50 20 L50 80 M20 50 L80 50 M29 29 L71 71 M29 71 L71 29" strokeWidth="0.8" />
    <circle cx="50" cy="50" r="8" fill="currentColor" />
  </svg>
);

// 21. Rueda Solar de Filigrana
export const SolarWheelGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="50" cy="50" r="46" />
    {Array.from({ length: 8 }).map((_, i) => {
      const a = (Math.PI / 4) * i;
      const x = 50 + Math.cos(a) * 24;
      const y = 50 + Math.sin(a) * 24;
      return <circle key={i} cx={x} cy={y} r="14" strokeWidth="0.6" />;
    })}
    <circle cx="50" cy="50" r="10" fill="currentColor" fillOpacity="0.2" />
  </svg>
);

// 22. Cruz de Espada y Lancetas
export const SwordCrossGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <line x1="50" y1="6" x2="50" y2="94" strokeWidth="2" />
    <line x1="20" y1="32" x2="80" y2="32" strokeWidth="2" />
    <circle cx="50" cy="32" r="16" strokeDasharray="2 2" />
    <polygon points="50,6 45,18 55,18" fill="currentColor" />
    <circle cx="50" cy="94" r="4" fill="currentColor" />
  </svg>
);

// 23. Portal de Vesica Piscis
export const VesicaPiscisGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <circle cx="34" cy="50" r="32" />
    <circle cx="66" cy="50" r="32" />
    <line x1="50" y1="10" x2="50" y2="90" strokeDasharray="2 2" strokeWidth="0.8" />
    <circle cx="50" cy="50" r="6" fill="currentColor" fillOpacity="0.3" />
  </svg>
);

// 24. Cáliz Sagrado Vectorial
export const ChaliceSigilGlyph = ({ className = 'w-10 h-10', size = 40 }: GlyphProps) => (
  <svg viewBox="0 0 100 100" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" className={className}>
    <path d="M25 18 Q25 60 50 62 Q75 60 75 18 Z" fill="currentColor" fillOpacity="0.15" />
    <line x1="50" y1="62" x2="50" y2="84" strokeWidth="2" />
    <path d="M28 92 L72 92" strokeWidth="2" />
    <circle cx="50" cy="38" r="8" strokeDasharray="1.5 1.5" />
  </svg>
);

// Export all 24 glyphs in an array catalog
export const ALL_GOTHIC_GLYPHS = [
  { id: 'quadrafoil', name: 'Cuadrifolio de Catedral', Component: QuadrafoilGlyph },
  { id: 'trefoil', name: 'Trifolio Ojival', Component: TrefoilGlyph },
  { id: 'hexagram', name: 'Hexagrama Sacro', Component: HexagramGlyph },
  { id: 'octagram', name: 'Octagrama del Santuario', Component: OctagramGlyph },
  { id: 'templar', name: 'Cruz Templaria Paté', Component: TemplarCrossGlyph },
  { id: 'solar_rosette', name: 'Rosetón Solar de 16 Rayos', Component: SolarRosetteGlyph },
  { id: 'fleur_de_lis', name: 'Flor de Lis Gótica', Component: FleurDeLisGlyph },
  { id: 'pointed_portal', name: 'Portal de Arco Ojival', Component: PointedArchPortalGlyph },
  { id: 'ogee_arch', name: 'Arco Conopial / Ogee', Component: OgeeArchGlyph },
  { id: 'vault_rib', name: 'Bóveda de Crucería', Component: VaultRibGlyph },
  { id: 'oculi', name: 'Óculo Gótico Central', Component: OculiGlyph },
  { id: 'saturn', name: 'Sello Alquímico de Saturno', Component: AlchemicalSaturnGlyph },
  { id: 'mason_compass', name: 'Compás del Maestro Cantero', Component: MasonCompassGlyph },
  { id: 'dodecagram', name: 'Dodecagrama de 12 Lancetas', Component: DodecagramGlyph },
  { id: 'pinnacle', name: 'Pináculo y Aguja Gótica', Component: PinnacleSpireGlyph },
  { id: 'gargoyle', name: 'Glifo de Gárgola Guardiana', Component: GargoyleSigilGlyph },
  { id: 'acanthus', name: 'Hoja de Acanto Gótica', Component: AcanthusLeafGlyph },
  { id: 'masonic_square', name: 'Escuadra y Compás Cantero', Component: MasonicSquareGlyph },
  { id: 'buttress', name: 'Arbotante y Contrafuerte', Component: ButtressArchGlyph },
  { id: 'crypt_seal', name: 'Sello Criptográfico Medieval', Component: CryptSealGlyph },
  { id: 'solar_wheel', name: 'Rueda Solar de Filigrana', Component: SolarWheelGlyph },
  { id: 'sword_cross', name: 'Cruz de Espada y Lancetas', Component: SwordCrossGlyph },
  { id: 'vesica_piscis', name: 'Portal de Vesica Piscis', Component: VesicaPiscisGlyph },
  { id: 'chalice', name: 'Cáliz Sagrado Vectorial', Component: ChaliceSigilGlyph },
];
