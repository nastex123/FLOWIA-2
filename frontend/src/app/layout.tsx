import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "FlowMind AI — Intelligent Process Automation (Local & Private)",
  description:
    "Transform spreadsheets and documents into structured, validated data using 100% local ML and deterministic pipelines.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="dark">
      <body className="bg-slate-950 text-slate-100 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
          FlowMind AI SaaS — 100% Local Machine Learning & Deterministic Processing
        </footer>
      </body>
    </html>
  );
}
