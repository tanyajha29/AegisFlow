import React from 'react';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';

const History = () => {
  const entries = [
    { id: 'SCAN-184', file: 'payments.py', date: '2026-03-04', score: 82, issues: 7, severity: 'High' },
    { id: 'SCAN-183', file: 'web/app.js', date: '2026-03-03', score: 89, issues: 4, severity: 'Medium' },
    { id: 'SCAN-182', file: 'api/users.go', date: '2026-03-02', score: 76, issues: 11, severity: 'Critical' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan History</p>
          <h1 className="text-3xl font-semibold text-white">Recent scans</h1>
          <p className="text-slate-500 text-sm">Filter by severity, date, or project.</p>
        </div>
        <div className="flex gap-3">
          <select className="bg-surface border border-border rounded-xl px-3 py-2 text-sm text-slate-200">
            <option>All severities</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
          <select className="bg-surface border border-border rounded-xl px-3 py-2 text-sm text-slate-200">
            <option>This month</option>
            <option>Last 30 days</option>
            <option>Last quarter</option>
          </select>
        </div>
      </div>

      <GlassCard className="p-4 overflow-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-slate-400">
            <tr className="border-b border-border">
              <th className="py-3">Scan ID</th>
              <th>File</th>
              <th>Date</th>
              <th>Risk Score</th>
              <th>Total Issues</th>
              <th>Severity</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border text-slate-200">
            {entries.map((item) => (
              <tr key={item.id}>
                <td className="py-3">{item.id}</td>
                <td>{item.file}</td>
                <td>{item.date}</td>
                <td className="text-accent font-semibold">{item.score}</td>
                <td>{item.issues}</td>
                <td><SeverityBadge level={item.severity} /></td>
                <td>
                  <button className="px-3 py-1 rounded-lg bg-white/5 text-xs border border-border">View report</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
};

export default History;
