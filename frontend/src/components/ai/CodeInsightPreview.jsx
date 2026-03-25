import React from 'react';

const variantStyles = {
  vulnerable: {
    title: 'Vulnerable Code',
    border: 'border-rose-400/40',
    bg: 'bg-rose-500/5',
    highlight: 'bg-rose-500/20 text-rose-50',
  },
  fixed: {
    title: 'Secure Fix',
    border: 'border-emerald-400/40',
    bg: 'bg-emerald-500/5',
    highlight: 'bg-emerald-500/20 text-emerald-50',
  },
};

const CodeInsightPreview = ({ code = '', lineNumber = null, variant = 'vulnerable', title }) => {
  const lines = (code || '').toString().split('\n');
  const styles = variantStyles[variant] || variantStyles.vulnerable;

  return (
    <div className={`rounded-xl border ${styles.border} bg-slate-900/80 shadow-inner shadow-black/30 overflow-hidden`}>
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/5 bg-slate-900/60">
        <div className="flex items-center gap-2 text-xs text-slate-200">
          <span className="h-2 w-2 rounded-full bg-rose-400"></span>
          <span className="h-2 w-2 rounded-full bg-amber-300"></span>
          <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
          <span className="font-semibold">{title || styles.title}</span>
        </div>
        {lineNumber ? (
          <span className="text-[11px] px-2 py-[2px] rounded-md bg-white/5 border border-white/10 text-slate-300">
            Line {lineNumber}
          </span>
        ) : null}
      </div>
      <div className="text-xs font-mono text-slate-100 overflow-auto max-h-64">
        {lines.length === 0 ? (
          <div className="px-3 py-2 text-slate-500">No code available.</div>
        ) : (
          <table className="min-w-full">
            <tbody>
              {lines.map((ln, idx) => {
                const lineNo = idx + 1;
                const isHighlight = lineNumber && lineNo === Number(lineNumber);
                return (
                  <tr key={idx} className={isHighlight ? styles.highlight : styles.bg}>
                    <td className="px-3 py-1 text-right align-top text-slate-500 select-none w-12">{lineNo}</td>
                    <td className="pr-3 py-1 whitespace-pre-wrap break-words">{ln || ' '}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default CodeInsightPreview;
