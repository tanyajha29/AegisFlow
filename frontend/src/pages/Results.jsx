import React, { useEffect, useState } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import GlassCard from '../components/GlassCard.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import { useScan } from '../context/ScanContext.jsx';
import ResultsFilter from '../components/ResultsFilter.jsx';
import VulnerabilityList from '../components/VulnerabilityList.jsx';
import AgentPanel from '../components/AgentPanel.jsx';

const Results = () => {
  const { lastResult } = useScan();
  const [downloading, setDownloading] = useState(false);
  const [toast, setToast] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

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
  const agentsUsed = lastResult.ai_agents_used || [];
  const aiLogs = lastResult.ai_logs || [];
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
        <GlassCard className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">Security Score</p>
            <p className="text-2xl font-semibold text-white">{Math.round(securityScore)}</p>
          </div>
          <ProgressBar value={securityScore} tone={band.tone} />
          <p className={`text-xs ${band.text}`}>{band.label}</p>
        </GlassCard>
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Severity Breakdown</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Critical</span><span className="text-critical font-semibold">{count('Critical')}</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>High</span><span className="text-high font-semibold">{count('High')}</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Medium</span><span className="text-medium font-semibold">{count('Medium')}</span>
            </div>
            <div className="flex items-center justify-between bg-white/5 rounded-xl px-3 py-2">
              <span>Low</span><span className="text-low font-semibold">{count('Low')}</span>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Risk Summary</p>
          <ul className="text-sm text-slate-300 space-y-1">
            <li>Total issues: {lastResult.total_findings ?? lastResult.total_issues}</li>
            <li>Risk level: {lastResult.risk_level || band.label}</li>
            <li>Scan id: {lastResult.scan_id}</li>
          </ul>
        </GlassCard>
      </div>
      <AgentPanel agentsUsed={agentsUsed} logs={aiLogs} />
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
    </div>
  );
};

export default Results;
