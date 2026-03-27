import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ClockIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import api from '../lib/api.js';

const SkeletonRow = () => (
  <tr>
    {[...Array(6)].map((_, i) => (
      <td key={i} className="py-3 pr-4">
        <div className="h-4 rounded bg-white/5 animate-pulse" style={{ width: `${60 + i * 10}%` }} />
      </td>
    ))}
  </tr>
);

const History = () => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api
      .get('/api/reports/history')
      .then((res) => setEntries(res.data.reports || []))
      .finally(() => setLoading(false));
  }, []);

  const filtered = entries.filter((e) => {
    const name = (e.display_file_name || e.file_name || '').toLowerCase();
    return name.includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-widest text-slate-500">Scan History</p>
          <h1 className="text-2xl font-bold text-white">Recent scans</h1>
          <p className="text-sm text-slate-500">Filter by severity, date, or project.</p>
        </div>
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search by filename…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-accent/40 w-56 transition"
          />
        </div>
      </div>

      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="border-b border-white/[0.06]">
                {['Scan ID', 'File', 'Date', 'Risk Score', 'Total Issues', 'Severity'].map((h) => (
                  <th key={h} className="py-3 px-4 text-[11px] uppercase tracking-widest text-slate-500 font-medium whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.04]">
              {loading ? (
                [...Array(5)].map((_, i) => <SkeletonRow key={i} />)
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-500">
                      <ClockIcon className="h-10 w-10 opacity-30" />
                      <p className="text-sm">
                        {search ? 'No scans match your search.' : 'No scan history yet. Run your first scan.'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map((item, idx) => (
                  <motion.tr
                    key={item.scan_id}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.03 }}
                    className="text-slate-300 hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="py-3 px-4 font-mono text-xs text-slate-500">#{item.scan_id}</td>
                    <td className="py-3 px-4 font-medium text-white max-w-[180px] truncate">
                      {item.display_file_name || item.file_name}
                    </td>
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                      {new Date(item.scan_date).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 font-semibold text-accent">{item.risk_score}</td>
                    <td className="py-3 px-4">{item.total_vulnerabilities}</td>
                    <td className="py-3 px-4">
                      <SeverityBadge level={item.risk_level?.includes('High') ? 'High' : 'Low'} />
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
};

export default History;
