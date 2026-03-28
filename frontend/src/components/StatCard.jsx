import React from 'react';
import { motion } from 'framer-motion';

const tones = {
  cyan: 'from-cyber/30 via-accent/20 to-white/0 text-accent',
  blue: 'from-blue-500/25 via-cyber/10 to-white/0 text-blue-300',
  green: 'from-emerald-400/25 via-emerald-500/10 to-white/0 text-emerald-300',
  amber: 'from-amber-400/25 via-amber-500/10 to-white/0 text-amber-300',
};

const StatCard = ({ title, value, subtext, icon: Icon, tone = 'cyan' }) => {
  const toneClass = tones[tone] || tones.cyan;

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-surface/80 backdrop-blur-xl p-5 shadow-[0_20px_60px_rgba(0,0,0,0.45)]"
    >
      <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${toneClass} opacity-50`} />
      <div className="pointer-events-none absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-cyber via-accent to-transparent opacity-70" />

      <div className="relative z-10 flex items-start justify-between gap-3">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold text-white">{value}</p>
          </div>
          {subtext && <p className="text-xs text-slate-400">{subtext}</p>}
        </div>
        {Icon && (
          <div className="h-11 w-11 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center shadow-[0_0_18px_rgba(34,211,238,0.25)]">
            <Icon className="h-5 w-5 text-white" />
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default StatCard;
