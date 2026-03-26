import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Download, Shield, AlertTriangle, AlertCircle,
  Info, FileText, Code2, BookOpen, Cpu, ChevronDown, ChevronUp,
} from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import api from '../lib/api.js';
import GlassCard from '../components/GlassCard.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';

// ─── helpers ────────────────────────────────────────────────────────────────

const s = (v, fallback = '—') => (v !== undefined && v !== null && v !== '' ? v : fallback);

const riskStyle = (level = '') => {
  if (level.includes('Critical')) return 'text-critical border-critical/50 bg-critical/10';
  if (level.includes('High'))     return 'text-high border-high/50 bg-high/10';
  if (level.includes('Medium'))   return 'text-medium border-medium/50 bg-medium/10';
  return 'text-low border-low/50 bg-low/10';
};

const severityIcon = (sev) => {
  if (sev === 'Critical') return <AlertTriangle size={14} className="text-critical" />;
  if (sev === 'High')     return <AlertCircle   size={14} className="text-high" />;
  if (sev === 'Medium')   return <Info          size={14} className="text-medium" />;
  return                         <Info          size={14} className="text-low" />;
};

// ─── sub-components ─────────────────────────────────────────────────────────

const StatCard = ({ label, value, sub, accent = false }) => (
  <GlassCard className={`p-4 space-y-1 ${accent ? 'border-accent/30' : ''}`}>
    <p className="text-xs uppercase tracking-widest text-slate-500">{label}</p>
    <p className={`text-2xl font-bold ${accent ? 'text-accent' : 'text-white'}`}>{s(value, '0')}</p>
    {sub && <p className="text-xs text-slate-400">{sub}</p>}
  </GlassCard>
);

const Section = ({ title, icon: Icon, children, className = '' }) => (
  <GlassCard className={`p-5 space-y-4 ${className}`}>
    <div className="flex items-center gap-2 border-b border-white/5 pb-3">
      {Icon && <Icon size={16} className="text-accent" />}
      <h2 className="text-sm font-semibold uppercase tracking-widest text-slate-300">{title}</h2>
    </div>
    {children}
  </GlassCard>
);

const CodeBlock = ({ code }) =>
  code ? (
    <pre className="bg-black/50 border border-white/5 rounded-lg p-3 text-xs text-slate-200 whitespace-pre-wrap overflow-x-auto font-mono leading-5">
      {code}
    </pre>
  ) : null;

const FindingCard = ({ finding, idx }) => {
  const [open, setOpen] = useState(false);
  const sev = finding.severity || 'Low';

  return (
    <div className="rounded-xl border border-white/8 bg-white/[0.03] overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition text-left"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-xs text-slate-600 font-mono w-5 flex-shrink-0">{idx + 1}</span>
          {severityIcon(sev)}
          <span className="text-sm font-medium text-white truncate">{s(finding.name || finding.type, 'Unknown Finding')}</span>
          {finding.file_name && (
            <span className="hidden sm:block text-xs text-slate-500 truncate">
              {finding.file_name}{finding.line_number ? `:${finding.line_number}` : ''}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          <SeverityBadge level={sev} />
          {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
        </div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-white/5 pt-3">
              {finding.file_name && (
                <p className="text-xs text-slate-400">
                  <span className="text-slate-600">File: </span>
                  {finding.file_name}
                  {finding.line_number ? ` · line ${finding.line_number}` : ''}
                </p>
              )}
              {finding.code_snippet && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Affected Code</p>
                  <CodeBlock code={finding.code_snippet} />
                </div>
              )}
              {finding.description && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Description</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{finding.description}</p>
                </div>
              )}
              {finding.impact && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Impact</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{finding.impact}</p>
                </div>
              )}
              {finding.attack_example && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Attack Example</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{finding.attack_example}</p>
                </div>
              )}
              {(finding.remediation || finding.recommendation) && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Recommendation</p>
                  <p className="text-sm text-slate-300 leading-relaxed">{finding.remediation || finding.recommendation}</p>
                </div>
              )}
              {finding.fix_code && (
                <div>
                  <p className="text-xs text-slate-500 mb-1">Fixed Code</p>
                  <CodeBlock code={finding.fix_code} />
                </div>
              )}
              {finding.cwe_reference && (
                <span className="inline-block px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-xs text-slate-400">
                  {finding.cwe_reference}
                </span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ─── skeleton ───────────────────────────────────────────────────────────────

const Skeleton = () => (
  <div className="space-y-6 animate-pulse">
    <div className="h-28 rounded-2xl bg-white/5" />
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-white/5" />)}
    </div>
    <div className="h-48 rounded-2xl bg-white/5" />
    <div className="h-64 rounded-2xl bg-white/5" />
  </div>
);

// ─── main page ──────────────────────────────────────────────────────────────

const ReportDetails = () => {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!scanId) return;
    setLoading(true);
    api
      .get(`/api/reports/${scanId}`)
      .then((res) => setReport(res.data))
      .catch((err) => setError(err?.response?.data?.detail || 'Report not found.'))
      .finally(() => setLoading(false));
  }, [scanId]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await api.get(`/api/reports/${scanId}/pdf`, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      a.href = url;
      a.download = `DristiScan_Report_${report?.file_name || scanId}_${stamp}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      // non-fatal
    } finally {
      setDownloading(false);
    }
  };

  if (loading) return <Skeleton />;

  if (error || !report) {
    return (
      <div className="space-y-4">
        <button
          type="button"
          onClick={() => navigate('/app/reports')}
          className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition"
        >
          <ArrowLeft size={15} /> Back to Reports
        </button>
        <GlassCard className="p-8 text-center space-y-2">
          <AlertCircle size={32} className="text-red-400 mx-auto" />
          <p className="text-white font-semibold">Report not found</p>
          <p className="text-slate-400 text-sm">{error || `Scan #${scanId} does not exist.`}</p>
        </GlassCard>
      </div>
    );
  }

  // Normalise fields — backend returns FullStructuredReportSchema
  const summary   = report.summary   || {};
  const findings  = report.findings  || [];
  const aiInsights = report.ai_insights || {};
  const riskScore  = report.risk_score || {};
  const secureVersion = report.secure_version || '';

  const fileName   = report.file_name || `Scan #${scanId}`;
  const scanDate   = report.scan_date ? new Date(report.scan_date).toLocaleString() : '—';
  const riskLevel  = summary.overall_risk || riskScore.reason || '—';
  const secScore   = typeof summary.security_score === 'number'
    ? summary.security_score
    : typeof riskScore.score === 'number'
    ? Math.max(0, 100 - riskScore.score * 10)
    : '—';

  // Split findings by category for dedicated sections
  const secretFindings = findings.filter((f) =>
    (f.category || '').toLowerCase().includes('secret') ||
    (f.name || '').toLowerCase().includes('secret') ||
    (f.name || '').toLowerCase().includes('key') ||
    (f.name || '').toLowerCase().includes('credential')
  );
  const depFindings = findings.filter((f) =>
    (f.category || '').toLowerCase().includes('depend') ||
    (f.name || '').toLowerCase().includes('depend')
  );
  const mainFindings = findings.filter(
    (f) => !secretFindings.includes(f) && !depFindings.includes(f)
  );

  const recommendations = report.recommendations || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* ── HERO ── */}
      <GlassCard className="p-6">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => navigate('/app/reports')}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition mb-1"
            >
              <ArrowLeft size={13} /> Back to Reports
            </button>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Security Analysis Report</p>
            <h1 className="text-2xl font-bold text-white leading-tight">{fileName}</h1>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span>Scan ID: <span className="text-slate-200">#{scanId}</span></span>
              <span>·</span>
              <span>Date: <span className="text-slate-200">{scanDate}</span></span>
              <span>·</span>
              <span className={`px-2 py-0.5 rounded-full border text-xs font-semibold ${riskStyle(riskLevel)}`}>
                {riskLevel}
              </span>
            </div>
            <p className="text-xs text-slate-600">Generated by DristiScan</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={handleDownload}
              disabled={downloading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent/10 border border-accent/30 text-accent text-sm hover:bg-accent/20 transition disabled:opacity-50"
            >
              <Download size={15} />
              {downloading ? 'Preparing…' : 'Download PDF'}
            </motion.button>
          </div>
        </div>
      </GlassCard>

      {/* ── SUMMARY CARDS ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Security Score" value={typeof secScore === 'number' ? `${Math.round(secScore)}` : secScore} sub="out of 100" accent />
        <StatCard label="Total Findings" value={summary.total ?? findings.length} />
        <StatCard label="Risk Level" value={riskLevel} />
        <StatCard label="Scan Engine" value="DristiScan v2" />
      </div>

      {/* ── EXECUTIVE SUMMARY ── */}
      <Section title="Executive Summary" icon={FileText}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Critical', value: summary.critical ?? 0, cls: 'text-critical' },
            { label: 'High',     value: summary.high     ?? 0, cls: 'text-high' },
            { label: 'Medium',   value: summary.medium   ?? 0, cls: 'text-medium' },
            { label: 'Low',      value: summary.low      ?? 0, cls: 'text-low' },
          ].map(({ label, value, cls }) => (
            <div key={label} className="rounded-xl bg-white/[0.03] border border-white/8 p-3 text-center">
              <p className={`text-2xl font-bold ${cls}`}>{value}</p>
              <p className="text-xs text-slate-500 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
        {aiInsights.summary && (
          <p className="text-sm text-slate-300 leading-relaxed border-t border-white/5 pt-4">
            {aiInsights.summary}
          </p>
        )}
      </Section>

      {/* ── AI INSIGHTS ── */}
      {(aiInsights.summary || aiInsights.most_critical_issue || aiInsights.fix_priority) && (
        <GlassCard className="p-5 border-accent/20 bg-accent/[0.03] space-y-4">
          <div className="flex items-center gap-2 border-b border-accent/10 pb-3">
            <Cpu size={16} className="text-accent" />
            <h2 className="text-sm font-semibold uppercase tracking-widest text-accent">AI Insights</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {aiInsights.summary && (
              <div className="space-y-1">
                <p className="text-xs text-slate-500 uppercase tracking-wide">Summary</p>
                <p className="text-sm text-slate-200 leading-relaxed">{aiInsights.summary}</p>
              </div>
            )}
            {aiInsights.most_critical_issue && (
              <div className="space-y-1">
                <p className="text-xs text-slate-500 uppercase tracking-wide">Most Dangerous</p>
                <p className="text-sm text-slate-200 leading-relaxed">{aiInsights.most_critical_issue}</p>
              </div>
            )}
            {aiInsights.fix_priority && (
              <div className="space-y-1">
                <p className="text-xs text-slate-500 uppercase tracking-wide">Fix Priority</p>
                <p className="text-sm text-slate-200 leading-relaxed">{aiInsights.fix_priority}</p>
              </div>
            )}
          </div>
        </GlassCard>
      )}

      {/* ── MAIN FINDINGS ── */}
      {mainFindings.length > 0 && (
        <Section title={`Vulnerability Findings (${mainFindings.length})`} icon={Shield}>
          <div className="space-y-2">
            {mainFindings.map((f, i) => (
              <FindingCard key={`main-${i}`} finding={f} idx={i} />
            ))}
          </div>
        </Section>
      )}

      {/* ── SECRET FINDINGS ── */}
      {secretFindings.length > 0 && (
        <Section title={`Secret Exposure (${secretFindings.length})`} icon={AlertTriangle}>
          <div className="space-y-2">
            {secretFindings.map((f, i) => (
              <FindingCard key={`secret-${i}`} finding={f} idx={i} />
            ))}
          </div>
        </Section>
      )}

      {/* ── DEPENDENCY FINDINGS ── */}
      {depFindings.length > 0 && (
        <Section title={`Dependency Issues (${depFindings.length})`} icon={Code2}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 uppercase border-b border-white/5">
                  <th className="text-left py-2 pr-4">Package</th>
                  <th className="text-left py-2 pr-4">Severity</th>
                  <th className="text-left py-2 pr-4">Description</th>
                  <th className="text-left py-2">Fix</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {depFindings.map((f, i) => (
                  <tr key={i} className="text-slate-300">
                    <td className="py-2 pr-4 font-mono text-xs">{f.name}</td>
                    <td className="py-2 pr-4"><SeverityBadge level={f.severity} /></td>
                    <td className="py-2 pr-4 text-xs text-slate-400">{f.description}</td>
                    <td className="py-2 text-xs text-slate-400">{f.remediation || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {/* ── RISK SCORE ── */}
      {(riskScore.score !== undefined || riskScore.reason) && (
        <Section title="Risk Score" icon={AlertCircle}>
          <div className="flex items-center gap-6">
            {riskScore.score !== undefined && (
              <div className="text-center">
                <p className="text-4xl font-bold text-white">{Number(riskScore.score).toFixed(1)}</p>
                <p className="text-xs text-slate-500 mt-1">out of 10</p>
              </div>
            )}
            {riskScore.reason && (
              <p className="text-sm text-slate-300 leading-relaxed">{riskScore.reason}</p>
            )}
          </div>
        </Section>
      )}

      {/* ── RECOMMENDATIONS ── */}
      {(recommendations.length > 0 || secureVersion) && (
        <Section title="Recommendations" icon={BookOpen}>
          {recommendations.length > 0 && (
            <ul className="space-y-2">
              {recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <span className="text-accent mt-0.5 flex-shrink-0">›</span>
                  {typeof rec === 'string' ? rec : rec.text || JSON.stringify(rec)}
                </li>
              ))}
            </ul>
          )}
          {secureVersion && (
            <div className="border-t border-white/5 pt-4">
              <p className="text-xs text-slate-500 mb-2 uppercase tracking-wide">Secure Code Suggestion</p>
              <CodeBlock code={secureVersion} />
            </div>
          )}
        </Section>
      )}

      {/* ── FOOTER ── */}
      <div className="text-center text-xs text-slate-600 py-4 space-y-1">
        <p>Generated by DristiScan · Scan #{scanId}</p>
        <p>{new Date().toLocaleString()}</p>
      </div>
    </motion.div>
  );
};

export default ReportDetails;
