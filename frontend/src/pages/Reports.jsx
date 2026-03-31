import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard.jsx';
import api from '../lib/api.js';
import ReportsList from '../components/ReportsList.jsx';
import SectionHeader from '../components/SectionHeader.jsx';
import { Button } from '../components/ui/button';

const Reports = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    api
      .get('/api/reports/history')
      .then((res) => {
        const list = res.data.reports || [];
        const sorted = [...list].sort(
          (a, b) => new Date(b.scan_date || 0) - new Date(a.scan_date || 0)
        );
        setRows(sorted);
      })
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

  const hasToggle = rows.length > 5;
  const visibleRows = showAll ? rows : rows.slice(0, 5);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Security Reports"
        title="DristiScan Reports"
        description="Polished PDFs ready for stakeholders. Filter, review, and export without leaving the command center."
        actions={
          hasToggle && (
            <Button
              variant="outline"
              size="sm"
              className="border-white/15 text-slate-100"
              onClick={() => setShowAll((v) => !v)}
            >
              {showAll ? 'Show Less' : 'Show All'}
            </Button>
          )
        }
      />

      {error && <GlassCard className="p-3 text-sm text-red-400 border-red-500/40 bg-red-500/10">{error}</GlassCard>}

      {loading ? (
        <GlassCard className="p-4 text-slate-300">Loading...</GlassCard>
      ) : (
        <ReportsList reports={visibleRows} onDownload={handleDownload} />
      )}
    </div>
  );
};

export default Reports;

