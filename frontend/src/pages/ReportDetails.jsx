import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Download, Shield, AlertTriangle, AlertCircle,
  Info, FileText, Code2, BookOpen, Cpu, ChevronDown, ChevronUp,
  CheckCircle2, Lock, ExternalLink, RefreshCw,
} from 'lucide-react';
// eslint-disable-next-line no-unused-vars
import { AnimatePresence, motion } from 'framer-motion';
import api from '../lib/api.js';
import { normalizeReport } from '../lib/reportMapper.js';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import ProgressBar from '../components/ProgressBar.jsx';

// ─── helpers ─────────────────────────────────────────────────────────────────

const fv = (v, fallback = '—') =>
  v !== undefined && v !== null && String(v).trim() !== '' ? v : fallback;

const riskStyle = (level = '') => {
  if (level.includes('Critical')) return { badge: 'text-red-300 border-red-500/40 bg-red-500/10',    bar: 'critical' };
  if (level.includes('High'))     return { badge: 'text-orange-300 border-orange-500/40 bg-orange-500/10', bar: 'danger' };
  if (level.includes('Medium'))   return { badge: 'text-yellow-300 border-yellow-500/40 bg-yellow-500/10', bar: 'warning' };
  return                                 { badge: 'text-green-300 border-green-500/40 bg-green-500/10',  bar: 'success' };
};

const sevIcon = (sev) => {
  const sz = 13;
  if (sev === 'Critical') return <AlertTriangle size={sz} className="text-red-400 flex-shrink-0" />;
  if (sev === 'High')     return <AlertCircle   size={sz} className="text-orange-400 flex-shrink-0" />;
  if (sev === 'Medium')   return <Info          size={sz} className="text-yellow-400 flex-shrink-0" />;
  return                         <CheckCircle2  size={sz} className="text-green-400 flex-shrink-0" />;
};

// ─── micro components ─────────────────────────────────────────────────────────

const Label = ({ children }) => (
  <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500 mb-1.5">{children}</p>
);

const CodeBlock = ({ code }) =>
  code ? (
    <pre className="bg-[#0a0f1a] border border-cyan-900/30 rounded-xl p-4 text-[11px] text-cyan-100/80 whitespace-pre-wrap overflow-x-auto font-mono leading-[1.7] shadow-inner">
      {code}
    </pre>
  ) : null;

const SectionHeader = ({ icon, title, count, accent = false }) => {
  const IconComp = icon;
  return (
    <div className={`flex items-center gap-3 pb-4 border-b ${accent ? 'border-cyan-500/15' : 'border-white/[0.06]'}`}>
      <div className={`h-8 w-8 rounded-xl flex items-center justify-center flex-shrink-0 ${accent ? 'bg-cyan-500/15' : 'bg-white/[0.05]'}`}>
        {IconComp && <IconComp size={15} className={accent ? 'text-cyan-400' : 'text-slate-400'} />}
      </div>
      <div className="flex items-baseline gap-2">
        <h2 className={`text-sm font-semibold ${accent ? 'text-cyan-300' : 'text-slate-200'}`}>{title}</h2>
        {count !== undefined && <span className="text-xs text-slate-600 font-mono">({count})</span>}
      </div>
    </div>
  );
};

const Panel = ({ children, className = '', accent = false }) => (
  <div className={`rounded-2xl border p-6 space-y-5 ${accent
    ? 'border-cyan-500/20 bg-gradient-to-br from-cyan-950/40 via-slate-900/60 to-slate-950/80 shadow-[0_0_40px_rgba(6,182,212,0.06)]'
    : 'border-white/[0.07] bg-white/[0.025] backdrop-blur-sm'
  } ${className}`}>
    {children}
  </div>
);

// ─── FindingCard ──────────────────────────────────────────────────────────────

const FindingCard = ({ finding, idx }) => {
  const [open, setOpen] = useState(false);
  const sev = finding.severity || 'Low';
  const sevColors = {
    Critical: 'border-l-red-500/60 bg-red-500/[0.03]',
    High:     'border-l-orange-500/60 bg-orange-500/[0.03]',
    Medium:   'border-l-yellow-500/60 bg-yellow-500/[0.03]',
    Low:      'border-l-green-500/60 bg-green-500/[0.03]',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.03, duration: 0.22 }}
      className={`rounded-xl border border-white/[0.07] border-l-2 ${sevColors[sev] || ''} overflow-hidden`}
    >
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3.5 hover:bg-white/[0.03] transition-colors text-left gap-3"
      >
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <span className="text-[10px] text-slate-700 font-mono w-4 flex-shrink-0">
            {String(idx + 1).padStart(2, '0')}
          </span>
          {sevIcon(sev)}
          <span className="text-sm font-medium text-white truncate">
            {fv(finding.name, 'Unknown Finding')}
          </span>
          {finding.file_name && (
            <span className="hidden md:block text-[11px] text-slate-600 font-mono truncate">
              {finding.file_name}{finding.line_number ? `:${finding.line_number}` : ''}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <SeverityBadge level={sev} />
          <div className="text-slate-600">
            {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </div>
        </div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-4 space-y-4 border-t border-white/[0.05]">
              {finding.file_name && (
                <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
                  <FileText size={11} />
                  {finding.file_name}{finding.line_number ? ` · line ${finding.line_number}` : ''}
                </div>
              )}
              {finding.code_snippet && (
                <div>
                  <Label>Affected Code</Label>
                  <CodeBlock code={finding.code_snippet} />
                </div>
              )}
              <div className="grid md:grid-cols-2 gap-4">
                {finding.description && (
                  <div>
                    <Label>Description</Label>
                    <p className="text-sm text-slate-300 leading-relaxed">{finding.description}</p>
                  </div>
                )}
                {finding.impact && (
                  <div>
                    <Label>Impact</Label>
                    <p className="text-sm text-slate-300 leading-relaxed">{finding.impact}</p>
                  </div>
                )}
              </div>
              {finding.attack_example && (
                <div>
                  <Label>Attack Example</Label>
                  <CodeBlock code={finding.attack_example} />
                </div>
              )}
              {finding.remediation && (
                <div>
                  <Label>Recommendation</Label>
                  <p className="text-sm text-slate-300 leading-relaxed">{finding.remediation}</p>
                </div>
              )}
              {finding.cwe_reference && (
                <div className="flex items-center gap-2 pt-1">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-slate-400 font-mono">
                    <Lock size={10} />{finding.cwe_reference}
                  </span>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-xs text-cyan-400">
                    <ExternalLink size={10} />OWASP
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// ─── Skeleton ─────────────────────────────────────────────────────────────────

const Skeleton = () => (
  <div className="space-y-6 animate-pulse">
    <div className="h-36 rounded-2xl bg-white/[0.04]" />
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => <div key={i} className="h-28 rounded-2xl bg-white/[0.04]" />)}
    </div>
    <div className="h-40 rounded-2xl bg-white/[0.04]" />
    <div className="h-32 rounded-2xl bg-cyan-950/20 border border-cyan-900/20" />
    {[...Array(3)].map((_, i) => <div key={i} className="h-14 rounded-xl bg-white/[0.03]" />)}
  </div>
);

// ─── Main Page ────────────────────────────────────────────────────────────────

const ReportDetails = () => {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);   // normalized report
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  const fetchReport = () => {
    if (!scanId) return;
    setLoading(true);
    setError('');
    api
      .get(`/api/reports/${scanId}`)
      .then(res => {
        const normalized = normalizeReport(res.data, scanId);
        if (import.meta.env.DEV) {
          console.debug('[ReportDetails] raw API response:', res.data);
          console.debug('[ReportDetails] normalized report:', normalized);
        }
        setReport(normalized);
      })
      .catch(err => {
        const msg = err?.response?.data?.detail || err?.message || 'Failed to load report.';
        setError(msg);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchReport(); }, [scanId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await api.get(`/api/reports/${scanId}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `DristiScan_Report_${report?.file_name || scanId}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a); a.click(); a.remove();
      window.URL.revokeObjectURL(url);
    } catch { /* non-fatal */ }
    finally { setDownloading(false); }
  };

  // ── loading ──────────────────────────────────────────────────────────────
  if (loading) return <Skeleton />;

  // ── error ────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="space-y-4">
        <button type="button" onClick={() => navigate('/app/reports')}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-white transition">
          <ArrowLeft size={14} /> Back to Reports
        </button>
        <GlassCard className="p-12 text-center space-y-4">
          <AlertCircle size={40} className="text-red-400 mx-auto" />
          <p className="text-white font-semibold text-lg">Could not load report</p>
          <p className="text-slate-400 text-sm">{error}</p>
          <button type="button" onClick={fetchReport}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.05] border border-white/10 text-sm text-slate-300 hover:bg-white/10 transition">
            <RefreshCw size={14} /> Retry
          </button>
        </GlassCard>
      </div>
    );
  }

  // ── not found / empty ────────────────────────────────────────────────────
  if (!report) {
    return (
      <div className="space-y-4">
        <button type="button" onClick={() => navigate('/app/reports')}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-white transition">
          <ArrowLeft size={14} /> Back to Reports
        </button>
        <GlassCard className="p-12 text-center space-y-3">
          <FileText size={40} className="text-slate-600 mx-auto" />
          <p className="text-white font-semibold">No report data available</p>
          <p className="text-slate-500 text-sm">Scan #{scanId} returned no report content.</p>
        </GlassCard>
      </div>
    );
  }

  // ── render ───────────────────────────────────────────────────────────────
  const { summary, findings, ai_insights, recommendations, secure_version } = report;

  const riskLevel = fv(summary.overall_risk, '');
  const secScore  = summary.security_score ?? 0;
  const risk      = riskStyle(riskLevel);
  const scanDate  = report.scan_date ? new Date(report.scan_date).toLocaleString() : '—';

  // split findings by category for dedicated sections
  const isSecret = f => ['secret','key','credential','token'].some(k =>
    (f.name||'').toLowerCase().includes(k) || (f.category||'').toLowerCase().includes(k));
  const isDep = f => ['depend','package','library'].some(k =>
    (f.name||'').toLowerCase().includes(k) || (f.category||'').toLowerCase().includes(k));

  const secretFindings = findings.filter(isSecret);
  const depFindings    = findings.filter(f => !isSecret(f) && isDep(f));
  const mainFindings   = findings.filter(f => !isSecret(f) && !isDep(f));

  const total = summary.total || findings.length || 1;
  const sevCounts = [
    { label: 'Critical', value: summary.critical, text: 'text-red-400',    border: 'border-red-500/25',    bg: 'bg-red-500/[0.06]',    bar: 'bg-red-500' },
    { label: 'High',     value: summary.high,     text: 'text-orange-400', border: 'border-orange-500/25', bg: 'bg-orange-500/[0.06]', bar: 'bg-orange-500' },
    { label: 'Medium',   value: summary.medium,   text: 'text-yellow-400', border: 'border-yellow-500/25', bg: 'bg-yellow-500/[0.06]', bar: 'bg-yellow-500' },
    { label: 'Low',      value: summary.low,      text: 'text-green-400',  border: 'border-green-500/25',  bg: 'bg-green-500/[0.06]',  bar: 'bg-green-500' },
  ];

  const hasAiInsights = ai_insights.summary || ai_insights.most_critical_issue || ai_insights.fix_priority;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 pb-10">

      {/* HERO */}
      <div className="rounded-2xl border border-white/[0.07] bg-gradient-to-br from-slate-900/80 via-slate-950/90 to-[#050d1a]/95 p-6 shadow-[0_0_60px_rgba(6,182,212,0.05)]">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-5">
          <div className="space-y-3 min-w-0">
            <button type="button" onClick={() => navigate('/app/reports')}
              className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-300 transition group">
              <ArrowLeft size={12} className="group-hover:-translate-x-0.5 transition-transform" />
              Back to Reports
            </button>
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-600/80 mb-1.5">Security Analysis Report</p>
              <h1 className="text-2xl md:text-3xl font-bold text-white leading-tight truncate">{report.file_name}</h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-3 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-slate-400 font-mono">#{scanId}</span>
              <span className="px-3 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-slate-400">{scanDate}</span>
              {riskLevel && (
                <span className={`px-3 py-1 rounded-lg border text-xs font-semibold ${risk.badge}`}>{riskLevel}</span>
              )}
              <span className="px-3 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-xs text-slate-500">DristiScan v2</span>
            </div>
          </div>
          <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
            onClick={handleDownload} disabled={downloading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/25 text-cyan-300 text-sm font-semibold hover:bg-cyan-500/20 transition disabled:opacity-50 flex-shrink-0 self-start">
            <Download size={15} />
            {downloading ? 'Preparing...' : 'Download PDF'}
          </motion.button>
        </div>
      </div>

      {/* SUMMARY CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Security Score', value: `${Math.round(secScore)}`, sub: 'out of 100', accent: true },
          { label: 'Total Findings', value: summary.total, sub: 'vulnerabilities detected' },
          { label: 'Risk Level',     value: riskLevel || '—', sub: 'overall assessment' },
          { label: 'Scan Engine',    value: 'DristiScan', sub: 'v2 · rule + AI' },
        ].map(({ label, value, sub, accent }) => (
          <div key={label} className={`rounded-2xl border p-5 space-y-2 ${accent
            ? 'border-cyan-500/20 bg-gradient-to-br from-cyan-950/40 to-slate-950/60'
            : 'border-white/[0.07] bg-white/[0.025]'}`}>
            <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500">{label}</p>
            <p className={`text-3xl font-bold leading-none ${accent ? 'text-cyan-300' : 'text-white'}`}>{value}</p>
            <p className="text-[11px] text-slate-600">{sub}</p>
            {accent && <div className="pt-1"><ProgressBar value={secScore} tone={risk.bar} /></div>}
          </div>
        ))}
      </div>

      {/* SEVERITY BREAKDOWN */}
      <Panel>
        <SectionHeader icon={Shield} title="Severity Breakdown" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {sevCounts.map(({ label, value, text, border, bg, bar }) => (
            <div key={label} className={`rounded-xl border ${border} ${bg} p-4 space-y-3`}>
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-500">{label}</p>
                <p className={`text-2xl font-bold ${text}`}>{value}</p>
              </div>
              <div className="w-full bg-white/[0.05] rounded-full h-1.5 overflow-hidden">
                <div className={`h-full rounded-full ${bar}`} style={{ width: `${Math.round((value / total) * 100)}%` }} />
              </div>
              <p className="text-[10px] text-slate-600">{Math.round((value / total) * 100)}% of findings</p>
            </div>
          ))}
        </div>
      </Panel>

      {/* AI INSIGHTS — only shown when backend provides real data */}
      {hasAiInsights && (
        <Panel accent>
          <SectionHeader icon={Cpu} title="AI Insights" accent />
          <div className="grid md:grid-cols-3 gap-5">
            {[
              { key: 'summary',             label: 'Analysis Summary' },
              { key: 'most_critical_issue', label: 'Most Dangerous Issue' },
              { key: 'fix_priority',        label: 'Fix Priority' },
            ].map(({ key, label }) => ai_insights[key] ? (
              <div key={key} className="space-y-2 p-4 rounded-xl bg-white/[0.03] border border-cyan-900/20">
                <Label>{label}</Label>
                <p className="text-sm text-slate-200 leading-relaxed">{ai_insights[key]}</p>
              </div>
            ) : null)}
          </div>
        </Panel>
      )}

      {/* MAIN FINDINGS */}
      {mainFindings.length > 0 ? (
        <Panel>
          <SectionHeader icon={Shield} title="Vulnerability Findings" count={mainFindings.length} />
          <div className="space-y-2">
            {mainFindings.map((finding, i) => <FindingCard key={`main-${i}`} finding={finding} idx={i} />)}
          </div>
        </Panel>
      ) : findings.length === 0 && (
        <Panel>
          <SectionHeader icon={Shield} title="Vulnerability Findings" />
          <p className="text-sm text-slate-500 text-center py-6">No findings recorded for this scan.</p>
        </Panel>
      )}

      {/* SECRET FINDINGS */}
      {secretFindings.length > 0 && (
        <Panel>
          <SectionHeader icon={AlertTriangle} title="Secret Exposure" count={secretFindings.length} />
          <div className="space-y-2">
            {secretFindings.map((finding, i) => <FindingCard key={`secret-${i}`} finding={finding} idx={i} />)}
          </div>
        </Panel>
      )}

      {/* DEPENDENCY FINDINGS */}
      {depFindings.length > 0 && (
        <Panel>
          <SectionHeader icon={Code2} title="Dependency Issues" count={depFindings.length} />
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/[0.06]">
                  {['Package', 'Severity', 'Description', 'Fix'].map(h => (
                    <th key={h} className="text-left py-3 pr-4 text-[10px] uppercase tracking-widest text-slate-500 font-semibold">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {depFindings.map((dep, i) => (
                  <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 pr-4 font-mono text-xs text-slate-300">{dep.name}</td>
                    <td className="py-3 pr-4"><SeverityBadge level={dep.severity} /></td>
                    <td className="py-3 pr-4 text-xs text-slate-400 max-w-xs">{dep.description}</td>
                    <td className="py-3 text-xs text-slate-400">{dep.remediation || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}

      {/* RECOMMENDATIONS */}
      {recommendations.length > 0 && (
        <Panel>
          <SectionHeader icon={BookOpen} title="Recommendations" />
          <ul className="space-y-3">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-slate-300 leading-relaxed">
                <span className="mt-0.5 h-5 w-5 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-[10px] font-bold text-cyan-400">{i + 1}</span>
                </span>
                {rec}
              </li>
            ))}
          </ul>
        </Panel>
      )}

      {/* SECURE VERSION */}
      {secure_version && (
        <Panel>
          <SectionHeader icon={Shield} title="Secure Code Suggestion" />
          <CodeBlock code={secure_version} />
        </Panel>
      )}

      {/* COMPLIANCE */}
      <Panel>
        <SectionHeader icon={Lock} title="Compliance & References" />
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { name: 'OWASP Top 10', desc: 'A03:2021 Injection · A02:2021 Cryptographic Failures · A05:2021 Security Misconfiguration', color: 'border-blue-500/20 bg-blue-500/[0.04]', text: 'text-blue-400' },
            { name: 'CWE Mapping',  desc: 'Common Weakness Enumeration references are shown on each finding card above.', color: 'border-purple-500/20 bg-purple-500/[0.04]', text: 'text-purple-400' },
            { name: 'CVSS Scoring', desc: 'Critical ≥ 9.0 · High 7.0–8.9 · Medium 4.0–6.9 · Low < 4.0', color: 'border-red-500/20 bg-red-500/[0.04]', text: 'text-red-400' },
          ].map(({ name, desc, color, text }) => (
            <div key={name} className={`rounded-xl border ${color} p-4 space-y-2`}>
              <p className={`text-xs font-semibold ${text}`}>{name}</p>
              <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </Panel>

      {/* FOOTER */}
      <div className="text-center py-6 space-y-1 border-t border-white/[0.04]">
        <p className="text-xs text-slate-700">Generated by DristiScan · Scan #{scanId}</p>
        <p className="text-xs text-slate-800">{new Date().toLocaleString()}</p>
      </div>

    </motion.div>
  );
};

export default ReportDetails;

