import React from 'react';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import { useScan } from '../context/ScanContext.jsx';

const Results = () => {
  const { lastResult } = useScan();

  if (!lastResult) {
    return (
      <div className="space-y-4">
        <p className="text-slate-300">No scan results yet. Run a scan first.</p>
      </div>
    );
  }

  const severities = lastResult.vulnerabilities || [];
  const count = (level) => severities.filter((v) => v.severity === level).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan Results</p>
          <h1 className="text-3xl font-semibold text-white">Findings for {lastResult.file_name}</h1>
          <p className="text-slate-500 text-sm">Security score and remediation-ready details.</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <GlassCard className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">Security Score</p>
            <p className="text-2xl font-semibold text-white">{lastResult.risk_score}</p>
          </div>
          <ProgressBar value={lastResult.risk_score} />
          <p className="text-xs text-slate-500">{lastResult.risk_level}</p>
        </GlassCard>
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Severity Breakdown</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Critical</span><span className="text-critical font-semibold">{count('Critical')}</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>High</span><span className="text-high font-semibold">{count('High')}</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Medium</span><span className="text-medium font-semibold">{count('Medium')}</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Low</span><span className="text-low font-semibold">{count('Low')}</span>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Risk Summary</p>
          <ul className="text-sm text-slate-300 space-y-1">
            <li>Total issues: {lastResult.total_issues}</li>
            <li>Risk level: {lastResult.risk_level}</li>
            <li>Scan id: {lastResult.scan_id}</li>
          </ul>
        </GlassCard>
      </div>

      <div className="space-y-3">
        {severities.length === 0 && (
          <GlassCard className="p-4 text-slate-300">No vulnerabilities detected in this scan.</GlassCard>
        )}
        {severities.map((v, idx) => (
          <GlassCard key={idx} className="p-4 hover:border-accent/40 transition">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <div className="flex items-center gap-3">
                  <p className="text-lg font-semibold text-white">{v.name}</p>
                  <SeverityBadge level={v.severity} />
                </div>
                <p className="text-xs text-slate-500">{v.file_name} · line {v.line_number ?? '—'}</p>
              </div>
            </div>
            <div className="mt-3 grid md:grid-cols-2 gap-3 text-sm">
              <div className="bg-white/5 rounded-xl p-3">
                <p className="text-slate-300 mb-1">Code Snippet</p>
                <pre className="text-xs font-mono text-slate-200 whitespace-pre-wrap">{v.code_snippet || 'N/A'}</pre>
              </div>
              <div className="space-y-1">
                <p className="text-slate-300">Explanation</p>
                <p className="text-slate-400 text-sm">{v.description}</p>
                <p className="text-slate-300 mt-2">Remediation</p>
                <p className="text-slate-400 text-sm">{v.remediation}</p>
              </div>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};

export default Results;
