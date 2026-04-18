import React, { useEffect, useState } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import GlassCard from '../components/GlassCard.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import { useScan } from '../context/ScanContext.jsx';
import ResultsFilter from '../components/ResultsFilter.jsx';
import VulnerabilityList from '../components/VulnerabilityList.jsx';
import SectionHeader from '../components/SectionHeader.jsx';
import { Button } from '../components/ui/button';

const Results = () => {
  const { lastResult } = useScan();
  const [downloading, setDownloading] = useState(false);
  const [toast, setToast] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [passphrase, setPassphrase] = useState('');
  const [passModal, setPassModal] = useState(false);
  const [passError, setPassError] = useState('');

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 2800);
    return () => clearTimeout(timer);
  }, [toast]);

  if (!lastResult) {
    return (
      <div className="space-y-4">
        <p className="text-slate-300">No scan results yet. Run a scan first.</p>
      </div>
    );
  }

  const severities = lastResult.vulnerabilities || [];
  const displayName = lastResult.display_file_name || lastResult.original_file_name || lastResult.file_name;
  const securityScore = lastResult.security_score ?? Math.max(0, 100 - (lastResult.risk_score ?? 0));
  const band =
    securityScore >= 80
      ? { tone: 'success', label: 'Low Risk', text: 'text-green-400' }
      : securityScore >= 50
        ? { tone: 'warning', label: 'Medium Risk', text: 'text-yellow-300' }
        : securityScore >= 20
          ? { tone: 'danger', label: 'High Risk', text: 'text-orange-400' }
          : { tone: 'critical', label: 'Critical Risk', text: 'text-red-400' };
  const count = (level) => lastResult?.[`${level.toLowerCase()}_count`] ?? severities.filter((v) => v.severity === level).length;

  const openProtected = () => {
    setPassError('');
    setPassModal(true);
  };

  const handleDownload = async () => {
    if (!lastResult?.scan_id) return;
    setDownloading(true);
    setPassError('');
    try {
      if (!passphrase || passphrase.length < 6) {
        setPassError('Passphrase must be at least 6 characters.');
        return;
      }
      const { default: api } = await import('../lib/api.js');
      const res = await api.post(
        `/api/reports/${lastResult.scan_id}/protected-pdf`,
        { passphrase },
        { responseType: 'blob' }
      );
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      a.href = url;
      a.download = `DristiScan_Report_${displayName || 'scan'}_${stamp}_protected.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setToast({ type: 'success', message: 'Protected report downloaded' });
      setPassphrase('');
      setPassModal(false);
    } catch (err) {
      setToast({ type: 'error', message: err.response?.data?.detail || 'Failed to generate protected PDF' });
    } finally {
      setDownloading(false);
    }
  };

  const openInsights = (finding, tab) => {
    setSelectedFinding(finding);
    setInsightsTab(tab);
    setInsightsOpen(true);
  };

  return (
    <div className="space-y-6 relative">
      {toast && (
        <div
          className={`fixed top-4 right-4 px-4 py-3 rounded-xl text-sm text-white shadow-glow ${
            toast.type === 'error' ? 'bg-red-600' : 'bg-green-600'
          }`}
        >
          {toast.message}
        </div>
      )}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <SectionHeader
          eyebrow="Scan Results"
          title={`Findings for ${displayName}`}
          description="Review severity, understand context, and export a polished report."
        />
        <Button
          type="button"
          onClick={openProtected}
          disabled={downloading}
          variant="outline"
          size="sm"
          className="h-11 px-4 border-white/15 text-slate-100 self-start md:self-auto"
        >
          {downloading ? (
            <svg className="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          ) : (
            <ArrowDownTrayIcon className="h-4 w-4" />
          )}
          <span>{downloading ? 'Preparing...' : 'Download Protected Report'}</span>
        </Button>
      </div>
      <div className="flex flex-wrap gap-3 text-xs text-slate-400">
        <span className="px-3 py-1 rounded-full border border-white/10 bg-white/5">Scan ID: {lastResult.scan_id}</span>
        <span className="px-3 py-1 rounded-full border border-white/10 bg-white/5">
          Risk: {lastResult.risk_level || band.label}
        </span>
        <span className="px-3 py-1 rounded-full border border-white/10 bg-white/5">
          Generated: {new Date().toLocaleString()}
        </span>
      </div>

      <div className="grid lg:grid-cols-3 gap-4 items-start">
        <GlassCard className="p-5 space-y-3 h-full">
          <p className="text-xs uppercase tracking-widest text-slate-500">Security Score</p>
          <div className="flex items-end gap-3">
            <p className="text-4xl font-bold text-white">{Math.round(securityScore)}</p>
            <p className="text-slate-500 text-sm mb-1">/ 100</p>
          </div>
          <ProgressBar value={securityScore} tone={band.tone} />
          <p className={`text-xs font-semibold ${band.text}`}>{band.label}</p>
        </GlassCard>
        <GlassCard className="p-5 space-y-3 h-full">
          <p className="text-xs uppercase tracking-widest text-slate-500">Severity Breakdown</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center justify-between rounded-xl border border-critical/20 bg-critical/5 px-3 py-2">
              <span className="text-slate-400 text-xs">Critical</span><span className="text-critical font-bold text-lg">{count('Critical')}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-high/20 bg-high/5 px-3 py-2">
              <span className="text-slate-400 text-xs">High</span><span className="text-high font-bold text-lg">{count('High')}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-medium/20 bg-medium/5 px-3 py-2">
              <span className="text-slate-400 text-xs">Medium</span><span className="text-medium font-bold text-lg">{count('Medium')}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-low/20 bg-low/5 px-3 py-2">
              <span className="text-slate-400 text-xs">Low</span><span className="text-low font-bold text-lg">{count('Low')}</span>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-5 space-y-3 h-full">
          <p className="text-xs uppercase tracking-widest text-slate-500">Risk Summary</p>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between py-1 border-b border-white/5">
              <span className="text-slate-400">Total issues</span>
              <span className="text-white font-semibold">{lastResult.total_findings ?? lastResult.total_issues}</span>
            </div>
            <div className="flex items-center justify-between py-1 border-b border-white/5">
              <span className="text-slate-400">Risk level</span>
              <span className="text-white font-semibold">{lastResult.risk_level || band.label}</span>
            </div>
            <div className="flex items-center justify-between py-1">
              <span className="text-slate-400">Scan ID</span>
              <span className="text-slate-300 font-mono text-xs">#{lastResult.scan_id}</span>
            </div>
          </div>
        </GlassCard>
      </div>
      <ResultsFilter
        selectedSeverity={selectedSeverity}
        onSeverityChange={setSelectedSeverity}
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
      />

      <VulnerabilityList
        vulnerabilities={severities}
        severity={selectedSeverity}
        search={searchTerm}
      />

      <PassphraseModal
        open={passModal}
        onClose={() => { setPassModal(false); setPassError(''); }}
        onSubmit={handleDownload}
        passphrase={passphrase}
        setPassphrase={setPassphrase}
        passError={passError}
        loading={downloading}
      />
    </div>
  );
};

export default Results;

const PassphraseModal = ({ open, onClose, onSubmit, passphrase, setPassphrase, passError, loading }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      {/* Modal — centered, not too wide */}
      <div className="relative z-10 bg-[#0d1526] border border-white/[0.1] rounded-2xl shadow-[0_0_60px_rgba(6,182,212,0.1)] max-w-md w-full p-6 space-y-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-white">Download Protected Report</h3>
            <p className="text-sm text-slate-400 mt-1">
              Set a passphrase to encrypt the PDF. You'll need it to open the file.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-500 hover:text-white transition p-1 rounded-lg hover:bg-white/5 flex-shrink-0"
          >
            ✕
          </button>
        </div>
        <div className="space-y-2">
          <label className="text-sm text-slate-300">Passphrase</label>
          <input
            type="password"
            value={passphrase}
            onChange={(e) => setPassphrase(e.target.value)}
            autoFocus
            className="w-full bg-white/[0.04] border border-white/[0.1] rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition"
            placeholder="At least 6 characters"
          />
          {passError && <p className="text-xs text-red-300">{passError}</p>}
        </div>
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.1] text-slate-200 hover:bg-white/[0.08] transition text-sm"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onSubmit}
            disabled={loading || !passphrase || passphrase.length < 6}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold shadow-[0_0_14px_rgba(6,182,212,0.25)] hover:shadow-[0_0_20px_rgba(6,182,212,0.35)] transition text-sm disabled:opacity-50"
          >
            {loading ? 'Preparing...' : 'Download protected PDF'}
          </button>
        </div>
      </div>
    </div>
  );
};
