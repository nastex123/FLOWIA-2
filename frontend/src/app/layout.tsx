import './globals.css';
import type { Metadata } from 'next';
import GothicBackdrop from '@/components/GothicBackdrop';

export const metadata: Metadata = {
  title: 'FlowMind AI — Catedral de Inteligencia Financiera',
  description: 'Automatización y Auditoría Local de Comprobantes',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <body className="bg-obsidian-950 text-slate-100 min-h-screen relative overflow-x-hidden font-sans">
        <GothicBackdrop />
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
