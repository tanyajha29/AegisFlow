import React from 'react';
import clsx from 'clsx';

const map = {
  Critical: 'bg-critical/15 text-critical border-critical/30',
  High: 'bg-high/15 text-high border-high/30',
  Medium: 'bg-medium/20 text-medium border-medium/40',
  Low: 'bg-low/15 text-low border-low/30',
};

const SeverityBadge = ({ level }) => (
  <span
    className={clsx(
      'text-xs font-semibold px-2.5 py-1 rounded-full border',
      map[level] || 'bg-slate-700/50 text-slate-200 border-slate-600/40'
    )}
  >
    {level}
  </span>
);

export default SeverityBadge;
