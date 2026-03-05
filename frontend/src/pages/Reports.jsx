import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import api from '../lib/api.js';

const Reports = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/reports/history')
      .then((res) => setRows(res.data.reports || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Security Reports</p>
          <h1 className="text-3xl font-semibold text-white">DristiScan Reports</h1>
          <p className="text-slate-500 text-sm">Export PDF/JSON and share with stakeholders.</p>
        </div>
      </div>

      <GlassCard className="p-4 overflow-auto">
        {loading ? (
          <p className="text-slate-300">Loading…</p>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="text-slate-400">
              <tr className="border-b border-border">
                <th className="py-3">Scan ID</th>
                <th>File</th>
                <th>Date</th>
                <th>Score</th>
                <th>Issues</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-slate-200">
              {rows.map((row) => (
                <tr key={row.scan_id}>
                  <td className="py-3">{row.scan_id}</td>
                  <td>{row.file_name}</td>
                  <td>{new Date(row.scan_date).toLocaleString()}</td>
                  <td className="text-accent font-semibold">{row.risk_score}</td>
                  <td>{row.total_vulnerabilities}</td>
                  <td><SeverityBadge level={row.risk_level?.includes('High') ? 'High' : 'Low'} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </GlassCard>
    </div>
  );
};

export default Reports;
