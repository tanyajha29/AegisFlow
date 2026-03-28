import React from 'react';

/**
 * Base glassmorphic card used everywhere for visual consistency with the landing page.
 */
const GlassCard = ({ children, className = '', tone = 'default' }) => {
  const toneOverlay =
    tone === 'accent'
      ? 'before:from-cyber/25 before:via-transparent before:to-accent/10'
      : 'before:from-white/10 before:via-transparent before:to-white/5';

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border border-white/10 bg-surface/70 backdrop-blur-xl shadow-[0_20px_60px_rgba(0,0,0,0.45)] transition-all hover:border-accent/30 hover:shadow-[0_20px_60px_rgba(37,99,235,0.28)] before:pointer-events-none before:absolute before:inset-0 before:bg-gradient-to-br before:opacity-60 before:content-[''] ${toneOverlay} ${className}`}
    >
      <div className="relative z-10">{children}</div>
    </div>
  );
};

export default GlassCard;
