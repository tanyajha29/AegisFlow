import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard.jsx';
import api from '../lib/api.js';
import ReportsList from '../components/ReportsList.jsx';
import SectionHeader from '../components/SectionHeader.jsx';

const Reports = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get('/api/reports/history')
      .then((res) => setRows(res.data.reports || []))
      .catch((err) => setError(err?.response?.data?.detail || 'Failed to load reports'))
      .finally(() => setLoading(false));
  }, []);

  const handleDownload = async (scanId, fileName) => {
    try {
      const res = await api.get(`/api/reports/${scanId}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      a.href = url;
      a.download = `DristiScan_Report_${fileName || 'scan'}_${stamp}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to download PDF');
    }
  };

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Security Reports"
        title="DristiScan Reports"
        description="Polished PDFs ready for stakeholders. Filter, review, and export without leaving the command center."
      />

      {error && <GlassCard className="p-3 text-sm text-red-400 border-red-500/40 bg-red-500/10">{error}</GlassCard>}

      {loading ? (
        <GlassCard className="p-4 text-slate-300">Loading...</GlassCard>
      ) : (
        <ReportsList reports={rows} onDownload={handleDownload} />
      )}
    </div>
  );
};

export default Reports;

