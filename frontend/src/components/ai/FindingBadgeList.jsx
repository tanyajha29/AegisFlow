import React from 'react';

const severityColors = {
  Critical: 'bg-rose-500/20 text-rose-100 border border-rose-400/40',
  High: 'bg-orange-500/20 text-orange-100 border border-orange-400/40',
  Medium: 'bg-amber-500/20 text-amber-100 border border-amber-400/40',
  Low: 'bg-emerald-500/20 text-emerald-100 border border-emerald-400/40',
};

const FindingBadgeList = ({ items = [] }) => {
  if (!items.length) return null;
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, idx) => {
        const sevClass = severityColors[item.severity] || severityColors.Medium;
        return (
          <span
            key={`${item.label}-${idx}`}
            className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${sevClass}`}
          >
            <span className="uppercase tracking-wide">{item.label}</span>
            <span className="text-[10px] px-2 py-[2px] rounded-full bg-white/10 border border-white/10">
              {item.severity}
            </span>
          </span>
        );
      })}
    </div>
  );
};

export default FindingBadgeList;
