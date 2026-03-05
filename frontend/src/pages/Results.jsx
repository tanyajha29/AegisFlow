import React from 'react';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import ProgressBar from '../components/ProgressBar.jsx';

const sampleVulns = [
  {
    name: 'SQL Injection',
    severity: 'Critical',
    file: 'api/users.py',
    line: 58,
    description: 'Dynamic SQL composed with unsanitized user input.',
    remediation: 'Use parameterized queries via ORM bind parameters.',
    snippet: "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
  },
  {
    name: 'Hardcoded AWS Key',
    severity: 'High',
    file: 'config.js',
    line: 12,
    description: 'AWS access key committed to repository.',
    remediation: 'Move secret to vault; rotate credentials.',
    snippet: "const AWS_KEY = 'AKIA...';",
  },
  {
    name: 'Outdated dependency',
    severity: 'Medium',
    file: 'requirements.txt',
    line: 5,
    description: 'Requests <2.32.0 vulnerable to header injection.',
    remediation: 'Upgrade requests to >= 2.32.0.',
    snippet: 'requests==2.28.1',
  },
];

const Results = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan Results</p>
          <h1 className="text-3xl font-semibold text-white">Vulnerability findings</h1>
          <p className="text-slate-500 text-sm">Security score, severity breakdown, and remediation-ready cards.</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 rounded-xl bg-white/5 border border-border text-slate-200">Export JSON</button>
          <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyber to-accent text-white shadow-glow">Download PDF</button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <GlassCard className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">Security Score</p>
            <p className="text-2xl font-semibold text-white">82</p>
          </div>
          <ProgressBar value={82} />
          <p className="text-xs text-slate-500">Low risk. Focus on critical + high items.</p>
        </GlassCard>
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Severity Breakdown</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Critical</span><span className="text-critical font-semibold">2</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>High</span><span className="text-high font-semibold">5</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Medium</span><span className="text-medium font-semibold">11</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Low</span><span className="text-low font-semibold">7</span>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Risk Summary</p>
          <ul className="text-sm text-slate-300 space-y-1">
            <li>• Critical: Immediate remediation required.</li>
            <li>• High: Patch within 7 days.</li>
            <li>• Medium: Add to sprint backlog.</li>
            <li>• Low: Monitor and document.</li>
          </ul>
        </GlassCard>
      </div>

      <div className="space-y-3">
        {sampleVulns.map((v, idx) => (
          <GlassCard key={idx} className="p-4 hover:border-accent/40 transition">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div>
                <div className="flex items-center gap-3">
                  <p className="text-lg font-semibold text-white">{v.name}</p>
                  <SeverityBadge level={v.severity} />
                </div>
                <p className="text-xs text-slate-500">{v.file} · line {v.line}</p>
              </div>
              <div className="text-right text-sm text-slate-400">
                <p>Detected by: SAST + Secrets</p>
                <p>Confidence: High</p>
              </div>
            </div>
            <div className="mt-3 grid md:grid-cols-2 gap-3 text-sm">
              <div className="bg-white/5 rounded-xl p-3">
                <p className="text-slate-300 mb-1">Code Snippet</p>
                <pre className="text-xs font-mono text-slate-200 whitespace-pre-wrap">{v.snippet}</pre>
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
