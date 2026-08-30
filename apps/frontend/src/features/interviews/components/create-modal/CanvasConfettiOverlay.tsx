/**
 * What: HTML5 Canvas Confetti animation layer.
 * Why: Fires a 60fps celebratory particle confetti burst when landing on Step 3.
 * Boundaries: Auto-cleans after 3.5s; 0kb external JS overhead.
 */

import React, { useEffect, useRef } from "react";

interface CanvasConfettiOverlayProps {
  isActive: boolean;
}

export const CanvasConfettiOverlay: React.FC<CanvasConfettiOverlayProps> = ({
  isActive,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (!isActive || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = (canvas.width = canvas.offsetWidth || 500);
    const height = (canvas.height = canvas.offsetHeight || 500);

    const colors = [
      "#FF5E62",
      "#FFD166",
      "#06D6A0",
      "#118AB2",
      "#8338EC",
      "#FF9F1C",
      "#E71D36",
    ];
    const particles = Array.from({ length: 65 }, () => ({
      x: width / 2 + (Math.random() - 0.5) * 80,
      y: height / 2 - 30 + (Math.random() - 0.5) * 40,
      vx: (Math.random() - 0.5) * 14,
      vy: Math.random() * -15 - 5,
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 12,
      shape: Math.random() > 0.4 ? "rect" : "circle",
    }));

    let animationFrameId: number;
    const startTime = performance.now();

    const render = (now: number) => {
      const elapsed = now - startTime;
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.38; // gravity
        p.vx *= 0.98; // air drag
        p.rotation += p.rotationSpeed;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rotation * Math.PI) / 180);
        ctx.fillStyle = p.color;

        if (p.shape === "rect") {
          ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.5);
        } else {
          ctx.beginPath();
          ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      });

      if (elapsed < 3500) {
        animationFrameId = requestAnimationFrame(render);
      }
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isActive]);

  if (!isActive) return null;

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 -z-0 w-full h-full overflow-hidden"
    />
  );
};
