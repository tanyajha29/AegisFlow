import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard.jsx';
import api from '../lib/api.js';
import ReportsList from '../components/ReportsList.jsx';
import SectionHeader from '../components/SectionHeader.jsx';
import { Button } from '../components/ui/button';
import { useAuth } from '../context/AuthContext.jsx';

const Reports = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadError, setDownloadError] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpNeeded, setOtpNeeded] = useState(false);

  const { user, verifyMfa } = useAuth();

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
      setDownloadError('');
      setOtpNeeded(false);

      let headers = {};
      if (user?.mfa_enabled) {
        if (!otp) {
          setOtpNeeded(true);
          setDownloadError('Enter your 6-digit OTP to download.');
          return;
        }
        await verifyMfa(otp);
        headers = { 'X-OTP': otp };
      }

      const res = await api.get(`/api/reports/${scanId}/pdf`, { responseType: 'blob', headers });
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
      if (user?.mfa_enabled) {
        setOtp('');
        setOtpNeeded(false);
      }
    } catch (err) {
      setDownloadError(err?.response?.data?.detail || 'Failed to download PDF');
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

      {user?.mfa_enabled && (
        <GlassCard className="p-3 flex flex-col gap-2 bg-white/5 border border-white/10">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Step-up download</p>
          <div className="flex flex-wrap items-center gap-3">
            <input
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              inputMode="numeric"
              pattern="[0-9]*"
              placeholder="OTP (6 digits)"
              className="w-full sm:w-48 bg-white/[0.04] border border-white/[0.08] rounded-xl px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent tracking-widest font-mono"
            />
            {otpNeeded && <span className="text-[11px] text-slate-500">Enter the current OTP to download.</span>}
          </div>
        </GlassCard>
      )}

      {error && <GlassCard className="p-3 text-sm text-red-400 border-red-500/40 bg-red-500/10">{error}</GlassCard>}
      {downloadError && (
        <GlassCard className="p-3 text-sm text-amber-300 border-amber-400/30 bg-amber-500/10">{downloadError}</GlassCard>
      )}

      {loading ? (
        <GlassCard className="p-4 text-slate-300">Loading...</GlassCard>
      ) : (
        <ReportsList reports={visibleRows} onDownload={handleDownload} />
      )}
    </div>
  );
};

export default Reports;

