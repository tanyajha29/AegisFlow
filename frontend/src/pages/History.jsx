import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import api from '../lib/api.js';

const History = () => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/reports/history')
      .then((res) => setEntries(res.data.reports || []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan History</p>
          <h1 className="text-3xl font-semibold text-white">Recent scans</h1>
          <p className="text-slate-500 text-sm">Filter by severity, date, or project.</p>
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
                <th>Risk Score</th>
                <th>Total Issues</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-slate-200">
              {entries.map((item) => (
                <tr key={item.scan_id}>
                  <td className="py-3">{item.scan_id}</td>
                  <td>{item.file_name}</td>
                  <td>{new Date(item.scan_date).toLocaleString()}</td>
                  <td className="text-accent font-semibold">{item.risk_score}</td>
                  <td>{item.total_vulnerabilities}</td>
                  <td><SeverityBadge level={item.risk_level?.includes('High') ? 'High' : 'Low'} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </GlassCard>
    </div>
  );
};

export default History;
