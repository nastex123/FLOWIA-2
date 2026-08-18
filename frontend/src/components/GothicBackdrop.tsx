'use client';

import React, { useEffect, useRef } from 'react';

interface Ember {
  x: number;
  y: number;
  radius: number;
  vx: number;
  vy: number;
  type: number; // 0 = crimson, 1 = violet, 2 = gold
  alpha: number;
  phase: number;
  speed: number;
}

export default function GothicBackdrop() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Initialize Embers
    const numEmbers = 45;
    const embers: Ember[] = Array.from({ length: numEmbers }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      radius: Math.random() * 2.2 + 1.0,
      vx: (Math.random() - 0.5) * 0.6,
      vy: -(Math.random() * 0.6 + 0.4),
      type: Math.random() > 0.4 ? 0 : Math.random() > 0.2 ? 1 : 2,
      alpha: Math.random() * 0.5 + 0.3,
      phase: Math.random() * Math.PI * 2,
      speed: Math.random() * 0.04 + 0.02,
    }));

    let roseAngle = 0;

    const drawRoseWindow = (
      cx: number,
      cy: number,
      radius: number,
      angle: number,
      alpha: number
    ) => {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(angle);

      // Concentric rings
      ctx.strokeStyle = `rgba(225, 29, 72, ${alpha * 0.8})`;
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.arc(0, 0, radius * 0.94, 0, Math.PI * 2);
      ctx.arc(0, 0, radius * 0.7, 0, Math.PI * 2);
      ctx.arc(0, 0, radius * 0.38, 0, Math.PI * 2);
      ctx.arc(0, 0, radius * 0.16, 0, Math.PI * 2);
      ctx.stroke();

      // 12 Petals
      const numPetals = 12;
      const petalR = radius * 0.28;
      ctx.strokeStyle = `rgba(245, 158, 11, ${alpha * 0.6})`;
      for (let i = 0; i < numPetals; i++) {
        const a = ((Math.PI * 2) / numPetals) * i;
        const px = Math.cos(a) * (radius * 0.68);
        const py = Math.sin(a) * (radius * 0.68);

        ctx.beginPath();
        ctx.arc(px, py, petalR, 0, Math.PI * 2);
        ctx.stroke();

        // Radial Spokes
        ctx.beginPath();
        ctx.moveTo(Math.cos(a) * (radius * 0.16), Math.sin(a) * (radius * 0.16));
        ctx.lineTo(Math.cos(a) * radius, Math.sin(a) * radius);
        ctx.stroke();
      }

      ctx.restore();
    };

    const render = () => {
      // Background base
      ctx.fillStyle = '#030408';
      ctx.fillRect(0, 0, width, height);

      roseAngle += 0.0015;

      // Draw Gothic Rose Windows
      drawRoseWindow(width * 0.75, height * 0.45, 280, roseAngle, 0.18);
      drawRoseWindow(width * 0.18, height * 0.82, 180, -roseAngle * 1.2, 0.12);

      // Connect near embers
      ctx.lineWidth = 0.8;
      for (let i = 0; i < numEmbers; i++) {
        for (let j = i + 1; j < numEmbers; j++) {
          const dx = embers[i].x - embers[j].x;
          const dy = embers[i].y - embers[j].y;
          const dist = Math.hypot(dx, dy);
          if (dist < 110) {
            const factor = 1 - dist / 110;
            ctx.strokeStyle = `rgba(190, 18, 60, ${factor * 0.25})`;
            ctx.beginPath();
            ctx.moveTo(embers[i].x, embers[i].y);
            ctx.lineTo(embers[j].x, embers[j].y);
            ctx.stroke();
          }
        }
      }

      // Update & Draw Embers
      for (const e of embers) {
        e.x += e.vx + Math.sin(e.phase) * 0.2;
        e.y += e.vy;
        e.phase += e.speed;

        if (e.y < 0) {
          e.y = height + 10;
          e.x = Math.random() * width;
        }
        if (e.x < 0) e.x = width;
        else if (e.x > width) e.x = 0;

        const currentAlpha = Math.max(
          0.1,
          Math.min(0.9, e.alpha + Math.sin(e.phase * 1.5) * 0.25)
        );

        let color = `rgba(251, 113, 133, ${currentAlpha})`;
        let halo = `rgba(225, 29, 72, ${currentAlpha * 0.3})`;
        if (e.type === 1) {
          color = `rgba(216, 180, 254, ${currentAlpha})`;
          halo = `rgba(147, 51, 234, ${currentAlpha * 0.25})`;
        } else if (e.type === 2) {
          color = `rgba(253, 230, 138, ${currentAlpha})`;
          halo = `rgba(217, 119, 6, ${currentAlpha * 0.3})`;
        }

        // Halo
        ctx.fillStyle = halo;
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.radius * 2.4, 0, Math.PI * 2);
        ctx.fill();

        // Core
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
    />
  );
}
