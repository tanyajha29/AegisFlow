import React, { useEffect, useState } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import GlassCard from '../components/GlassCard.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import { useScan } from '../context/ScanContext.jsx';
import ResultsFilter from '../components/ResultsFilter.jsx';
import VulnerabilityList from '../components/VulnerabilityList.jsx';
import AIInsightsDrawer from '../components/ai/AIInsightsDrawer.jsx';

const Results = () => {
  const { lastResult } = useScan();
  const [downloading, setDownloading] = useState(false);
  const [toast, setToast] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [insightsOpen, setInsightsOpen] = useState(false);
  const [insightsTab, setInsightsTab] = useState('explain');
  const [selectedFinding, setSelectedFinding] = useState(null);

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

  const handleDownload = async () => {
    if (!lastResult?.scan_id) return;
    setDownloading(true);
    try {
      const { default: api } = await import('../lib/api.js');
      const res = await api.get(`/api/reports/${lastResult.scan_id}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      a.href = url;
      a.download = `DristiScan_Report_${displayName || 'scan'}_${stamp}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setToast({ type: 'success', message: 'Report downloaded' });
    } catch (err) {
      setToast({ type: 'error', message: err.response?.data?.detail || 'Failed to generate PDF' });
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
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan Results</p>
          <div className="text-3xl font-semibold text-white leading-tight">
            <div className="text-base text-slate-400 mb-1">Findings for</div>
            <div>{displayName}</div>
          </div>
          <div className="flex flex-wrap gap-3 text-xs text-slate-400 mt-2">
            <span className="px-2 py-1 rounded-md border border-border bg-white/5">Scan ID: {lastResult.scan_id}</span>
            <span className="px-2 py-1 rounded-md border border-border bg-white/5">
              Risk: {lastResult.risk_level || band.label}
            </span>
            <span className="px-2 py-1 rounded-md border border-border bg-white/5">
              Generated: {new Date().toLocaleString()}
            </span>
          </div>
        </div>
        <button
          type="button"
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-border text-slate-100 hover:border-accent/60 transition disabled:opacity-60"
        >
          {downloading ? (
            <svg className="h-5 w-5 animate-spin text-white" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          ) : (
            <ArrowDownTrayIcon className="h-5 w-5" />
          )}
          <span>{downloading ? 'Preparing...' : 'Download Report'}</span>
        </button>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <GlassCard className="p-5 space-y-3">
          <p className="text-xs uppercase tracking-widest text-slate-500">Security Score</p>
          <div className="flex items-end gap-3">
            <p className="text-4xl font-bold text-white">{Math.round(securityScore)}</p>
            <p className="text-slate-500 text-sm mb-1">/ 100</p>
          </div>
          <ProgressBar value={securityScore} tone={band.tone} />
          <p className={`text-xs font-semibold ${band.text}`}>{band.label}</p>
        </GlassCard>
        <GlassCard className="p-5 space-y-3">
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
        <GlassCard className="p-5 space-y-3">
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
        onExplain={(v) => openInsights(v, 'explain')}
        onFix={(v) => openInsights(v, 'fix')}
      />

      <AIInsightsDrawer
        isOpen={insightsOpen}
        onClose={() => setInsightsOpen(false)}
        finding={selectedFinding}
        initialTab={insightsTab}
      />
    </div>
  );
};

export default Results;
