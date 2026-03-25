import React from 'react';

const InsightSectionCard = ({ title, children }) => (
  <div className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm p-4 shadow-lg shadow-cyan-900/10">
    <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">{title}</div>
    <div className="text-sm text-slate-100 whitespace-pre-wrap leading-relaxed">{children || 'Not provided.'}</div>
  </div>
);

export default InsightSectionCard;
