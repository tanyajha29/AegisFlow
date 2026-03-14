import React from 'react';

const toneClass = {
  gradient: 'bg-gradient-to-r from-cyber via-accent to-cyber',
  success: 'bg-green-500',
  warning: 'bg-yellow-400',
  danger: 'bg-orange-500',
  critical: 'bg-red-500',
};

const ProgressBar = ({ value, tone = 'gradient' }) => {
  const safeValue = Math.min(100, Math.max(0, value || 0));
  const barClass = toneClass[tone] || toneClass.gradient;
  return (
    <div className="w-full bg-surface border border-border rounded-full h-2 overflow-hidden">
      <div className={`h-full transition-all ${barClass}`} style={{ width: `${safeValue}%` }} />
    </div>
  );
};

export default ProgressBar;
