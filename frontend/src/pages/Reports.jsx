import React from 'react';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';

const rows = [
  { id: 'SCAN-184', file: 'payments.py', date: '2026-03-04', score: 82, issues: 7, critical: 1, high: 2, status: 'Ready' },
  { id: 'SCAN-183', file: 'web/app.js', date: '2026-03-03', score: 89, issues: 4, critical: 0, high: 1, status: 'Ready' },
  { id: 'SCAN-182', file: 'api/users.go', date: '2026-03-02', score: 76, issues: 11, critical: 2, high: 3, status: 'Ready' },
];

const Reports = () => (
  <div className="space-y-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Security Reports</p>
        <h1 className="text-3xl font-semibold text-white">Executive-ready reporting</h1>
        <p className="text-slate-500 text-sm">Export PDF/JSON and share with stakeholders.</p>
      </div>
      <div className="flex gap-3">
        <button className="px-4 py-2 rounded-xl bg-white/5 border border-border text-slate-200">Export JSON</button>
        <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyber to-accent text-white shadow-glow">Download PDF</button>
      </div>
    </div>

    <GlassCard className="p-4 overflow-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-slate-400">
          <tr className="border-b border-border">
            <th className="py-3">Scan ID</th>
            <th>File</th>
            <th>Date</th>
            <th>Score</th>
            <th>Issues</th>
            <th>Critical</th>
            <th>High</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border text-slate-200">
          {rows.map((row) => (
            <tr key={row.id}>
              <td className="py-3">{row.id}</td>
              <td>{row.file}</td>
              <td>{row.date}</td>
              <td className="text-accent font-semibold">{row.score}</td>
              <td>{row.issues}</td>
              <td className="text-critical">{row.critical}</td>
              <td className="text-high">{row.high}</td>
              <td><SeverityBadge level="Low" /></td>
              <td>
                <div className="flex gap-2">
                  <button className="px-3 py-1 rounded-lg bg-white/5 text-xs border border-border">View</button>
                  <button className="px-3 py-1 rounded-lg bg-cyber/20 text-xs border border-accent/50">PDF</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </GlassCard>
  </div>
);

export default Reports;
