import { useEffect, useMemo, useState } from 'react';
import { XMarkIcon, ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';
import {
  Sparkles, AlertTriangle, AlertCircle, Info, CheckCircle2,
  FileCode2, Lock, ExternalLink, RefreshCw, ChevronRight,
} from 'lucide-react';
import { explainVulnerability, suggestFix } from '../../lib/rag.js';

// ─── design tokens ───────────────────────────────────────────────────────────

const SEV = {
  Critical: { badge: 'text-red-300 border-red-500/40 bg-red-500/10',    dot: 'bg-red-500',    icon: AlertTriangle },
  High:     { badge: 'text-orange-300 border-orange-500/40 bg-orange-500/10', dot: 'bg-orange-500', icon: AlertCircle },
  Medium:   { badge: 'text-yellow-300 border-yellow-500/40 bg-yellow-500/10', dot: 'bg-yellow-500', icon: Info },
  Low:      { badge: 'text-green-300 border-green-500/40 bg-green-500/10',  dot: 'bg-green-500',  icon: CheckCircle2 },
};
const sevStyle = (s) => SEV[s] || SEV.Medium;

// ─── micro components ────────────────────────────────────────────────────────

const Label = ({ children }) => (
  <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-500 mb-2">{children}</p>
);

const Card = ({ children, className = '' }) => (
  <div className={`rounded-xl border border-white/[0.07] bg-white/[0.03] p-4 space-y-2 ${className}`}>
    {children}
  </div>
);

const RefBadge = ({ label, source }) => (
  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/50 text-[11px] text-slate-400 font-mono">
    <Lock size={9} className="text-slate-600" />
    {label}
    {source && <span className="text-slate-600">· {source}</span>}
  </span>
);

// ─── Code block with line numbers + highlight ────────────────────────────────

const CodeBlock = ({ code = '', highlightLine = null, variant = 'neutral', title }) => {
  const lines = String(code || '').split('\n');
  const variantCfg = {
    vulnerable: { border: 'border-red-500/25',     header: 'bg-red-950/40',    dot: 'bg-red-500',    hlRow: 'bg-red-500/20 border-l-2 border-red-500' },
    fixed:      { border: 'border-emerald-500/25', header: 'bg-emerald-950/40', dot: 'bg-emerald-500', hlRow: 'bg-emerald-500/20 border-l-2 border-emerald-500' },
    neutral:    { border: 'border-cyan-900/30',    header: 'bg-slate-900/60',   dot: 'bg-cyan-500',   hlRow: 'bg-cyan-500/10' },
  };
  const cfg = variantCfg[variant] || variantCfg.neutral;

  return (
    <div className={`rounded-xl border ${cfg.border} overflow-hidden shadow-inner shadow-black/40`}>
      {/* editor chrome */}
      <div className={`flex items-center justify-between px-3 py-2 border-b border-white/[0.05] ${cfg.header}`}>
        <div className="flex items-center gap-2">
          <span className="flex gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
            <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/70" />
            <span className="h-2.5 w-2.5 rounded-full bg-green-500/70" />
          </span>
          <span className="text-[11px] text-slate-500 font-mono ml-1">{title || 'code'}</span>
        </div>
        {highlightLine && (
          <span className={`text-[10px] px-2 py-0.5 rounded-md border border-white/10 bg-white/[0.04] text-slate-400 font-mono`}>
            line {highlightLine}
          </span>
        )}
      </div>
      {/* lines */}
      <div className="overflow-auto max-h-56 bg-[#080e1a]">
        <table className="min-w-full text-xs font-mono">
          <tbody>
            {lines.map((ln, i) => {
              const lineNo = i + 1;
              const isHl = highlightLine && lineNo === Number(highlightLine);
              return (
                <tr key={i} className={isHl ? cfg.hlRow : 'hover:bg-white/[0.02]'}>
                  <td className="pl-3 pr-4 py-0.5 text-right text-slate-700 select-none w-10 align-top">{lineNo}</td>
                  <td className="pr-4 py-0.5 text-slate-200 whitespace-pre-wrap break-words leading-5">{ln || ' '}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ─── Loading skeleton ────────────────────────────────────────────────────────

const LoadingSkeleton = () => (
  <div className="space-y-3 animate-pulse">
    <div className="h-28 rounded-xl bg-white/[0.04]" />
    <div className="h-3 rounded-full bg-white/[0.04] w-2/3" />
    <div className="h-20 rounded-xl bg-white/[0.04]" />
    <div className="h-20 rounded-xl bg-white/[0.04]" />
    <div className="h-16 rounded-xl bg-white/[0.04]" />
    <div className="h-3 rounded-full bg-white/[0.04] w-1/2" />
    <div className="h-24 rounded-xl bg-white/[0.04]" />
  </div>
);

// ─── Error block ─────────────────────────────────────────────────────────────

const ErrorBlock = ({ message, onRetry }) => (
  <div className="rounded-xl border border-red-500/25 bg-red-500/[0.06] p-5 space-y-3">
    <div className="flex items-start gap-3">
      <AlertTriangle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
      <div>
        <p className="text-sm font-semibold text-red-300">AI insights unavailable</p>
        <p className="text-xs text-red-400/70 mt-1 leading-relaxed">{message}</p>
      </div>
    </div>
    {onRetry && (
      <button type="button" onClick={onRetry}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/10 text-xs text-slate-300 hover:bg-white/10 transition">
        <RefreshCw size={11} /> Retry
      </button>
    )}
  </div>
);

// ─── Main drawer ─────────────────────────────────────────────────────────────

const AIInsightsDrawer = ({ isOpen, onClose, finding, initialTab = 'explain' }) => {
  const [activeTab, setActiveTab]       = useState(initialTab);
  const [explainData, setExplainData]   = useState(null);
  const [fixData, setFixData]           = useState(null);
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [loadingFix, setLoadingFix]     = useState(false);
  const [errorExplain, setErrorExplain] = useState(null);
  const [errorFix, setErrorFix]         = useState(null);
  const [copiedFixed, setCopiedFixed]   = useState(false);

  // ── reset on finding change ──────────────────────────────────────────────
  useEffect(() => {
    setExplainData(null); setFixData(null);
    setErrorExplain(null); setErrorFix(null);
    setLoadingExplain(false); setLoadingFix(false);
    setCopiedFixed(false);
  }, [finding]);

  useEffect(() => setActiveTab(initialTab), [initialTab, isOpen]);

  // ── API calls ────────────────────────────────────────────────────────────
  const runExplain = async () => {
    if (!finding || explainData || loadingExplain) return;
    setLoadingExplain(true); setErrorExplain(null);
    try { setExplainData(await explainVulnerability(finding)); }
    catch (err) { setErrorExplain(err.response?.data?.detail || err.message || 'Unknown error'); }
    finally { setLoadingExplain(false); }
  };

  const runFix = async () => {
    if (!finding || fixData || loadingFix) return;
    setLoadingFix(true); setErrorFix(null);
    try { setFixData(await suggestFix(finding)); }
    catch (err) { setErrorFix(err.response?.data?.detail || err.message || 'Unknown error'); }
    finally { setLoadingFix(false); }
  };

  useEffect(() => {
    if (!isOpen) return;
    if (activeTab === 'explain') runExplain();
    if (activeTab === 'fix') runFix();
  }, [activeTab, isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleCopyFixed = () => {
    if (!fixData?.fixed_code) return;
    navigator.clipboard.writeText(fixData.fixed_code).then(
      () => { setCopiedFixed(true); setTimeout(() => setCopiedFixed(false), 1500); },
      () => setCopiedFixed(false),
    );
  };

  // ── severity styling ─────────────────────────────────────────────────────
  const sev = finding?.severity || 'Medium';
  const sevCfg = useMemo(() => sevStyle(sev), [sev]);
  const SevIcon = sevCfg.icon;

  const lineNo = finding?.line_number || finding?.line || null;
  const codeSnippet = finding?.code_snippet || finding?.code || '';
  const fileName = finding?.file_name || finding?.file || 'unknown';

  // ── render explain ───────────────────────────────────────────────────────
  const renderExplain = () => {
    if (loadingExplain) return <LoadingSkeleton />;
    if (errorExplain)   return <ErrorBlock message={errorExplain} onRetry={runExplain} />;
    if (!explainData)   return <p className="text-sm text-slate-600 text-center py-8">No explanation available.</p>;

    return (
      <div className="space-y-3">
        {/* vulnerable code preview */}
        {codeSnippet && (
          <CodeBlock code={codeSnippet} highlightLine={lineNo} variant="vulnerable"
            title={`${fileName}${lineNo ? `:${lineNo}` : ''}`} />
        )}

        {/* grounding pill */}
        {explainData.retrieved_context_count > 0 && (
          <div className="flex items-center gap-2 text-[11px] text-slate-500">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-500 animate-pulse" />
            Grounded using {explainData.retrieved_context_count} knowledge source{explainData.retrieved_context_count === 1 ? '' : 's'}
          </div>
        )}

        {/* section cards */}
        <Card>
          <Label>Summary</Label>
          <p className="text-sm text-slate-200 leading-relaxed">{explainData.summary || 'Not provided.'}</p>
        </Card>

        <Card>
          <Label>Technical Explanation</Label>
          <p className="text-sm text-slate-300 leading-relaxed">{explainData.technical_explanation || 'Not provided.'}</p>
        </Card>

        <div className="grid grid-cols-2 gap-3">
          <Card>
            <Label>Impact</Label>
            <p className="text-sm text-slate-300 leading-relaxed">{explainData.impact || 'Not provided.'}</p>
          </Card>
          <Card>
            <Label>Exploit Scenario</Label>
            <p className="text-sm text-slate-300 leading-relaxed">{explainData.exploit_scenario || 'Not provided.'}</p>
          </Card>
        </div>

        <Card className="border-cyan-500/15 bg-cyan-950/20">
          <Label>Recommendation</Label>
          <p className="text-sm text-slate-200 leading-relaxed">{explainData.fix_recommendation || 'Not provided.'}</p>
        </Card>

        {explainData.secure_example && (
          <div>
            <Label>Secure Example</Label>
            <CodeBlock code={explainData.secure_example} variant="fixed" title="secure pattern" />
          </div>
        )}

        {explainData.references?.length > 0 && (
          <div>
            <Label>References</Label>
            <div className="flex flex-wrap gap-2">
              {explainData.references.map((ref, i) => (
                <RefBadge key={i} label={ref.label} source={ref.source} />
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // ── render fix ───────────────────────────────────────────────────────────
  const renderFix = () => {
    if (loadingFix) return <LoadingSkeleton />;
    if (errorFix)   return <ErrorBlock message={errorFix} onRetry={runFix} />;
    if (!fixData)   return <p className="text-sm text-slate-600 text-center py-8">No fix suggestion available.</p>;

    return (
      <div className="space-y-3">
        {/* before / after code */}
        <div className="space-y-2">
          {codeSnippet && (
            <CodeBlock code={codeSnippet} highlightLine={lineNo} variant="vulnerable"
              title={`before · ${fileName}`} />
          )}
          {fixData.fixed_code && (
            <CodeBlock code={fixData.fixed_code} variant="fixed" title="after · secure fix" />
          )}
        </div>

        <Card>
          <Label>Fix Summary</Label>
          <p className="text-sm text-slate-200 leading-relaxed">{fixData.fix_summary || 'Not provided.'}</p>
        </Card>

        <Card>
          <Label>Why This Fix Is Safer</Label>
          <p className="text-sm text-slate-300 leading-relaxed">{fixData.why_this_fix_is_safer || 'Not provided.'}</p>
        </Card>

        {fixData.notes?.length > 0 && (
          <Card>
            <Label>Notes</Label>
            <ul className="space-y-1.5">
              {fixData.notes.map((n, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <ChevronRight size={13} className="text-cyan-600 flex-shrink-0 mt-0.5" />
                  {n}
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* copy fixed code */}
        {fixData.fixed_code && (
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                <p className="text-[11px] uppercase tracking-widest text-emerald-500/70">Secure snippet</p>
              </div>
              <button type="button" onClick={handleCopyFixed}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/10 text-xs text-slate-300 hover:bg-white/10 transition">
                {copiedFixed
                  ? <><CheckIcon className="h-3.5 w-3.5 text-emerald-400" /> Copied!</>
                  : <><ClipboardIcon className="h-3.5 w-3.5" /> Copy code</>
                }
              </button>
            </div>
            <pre className="text-xs font-mono text-emerald-100/80 whitespace-pre-wrap leading-5 overflow-x-auto max-h-36">
              {fixData.fixed_code}
            </pre>
          </div>
        )}

        {fixData.references?.length > 0 && (
          <div>
            <Label>References</Label>
            <div className="flex flex-wrap gap-2">
              {fixData.references.map((ref, i) => (
                <RefBadge key={i} label={ref.label} source={ref.source} />
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // ── drawer shell ─────────────────────────────────────────────────────────
  return (
    <div className={`fixed inset-0 z-50 ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`}
      aria-hidden={!isOpen}>

      {/* backdrop */}
      <div onClick={onClose}
        className={`absolute inset-0 bg-black/75 backdrop-blur-sm transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0'}`} />

      {/* panel */}
      <div className={`absolute right-0 top-0 h-full w-full max-w-[640px] flex flex-col
        bg-[#060c18] border-l border-cyan-400/[0.08]
        shadow-[-20px_0_80px_rgba(6,182,212,0.07)]
        transform transition-transform duration-300 ease-out
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>

        {/* ── HEADER ── */}
        <div className="flex-shrink-0 px-6 pt-5 pb-4 border-b border-white/[0.06]
          bg-gradient-to-b from-slate-900/60 to-transparent">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2.5 min-w-0 flex-1">
              {/* label row */}
              <div className="flex items-center gap-2">
                <Sparkles size={13} className="text-cyan-400 flex-shrink-0" />
                <span className="text-[10px] uppercase tracking-[0.2em] text-cyan-600/80">AI Insights · DristiScan</span>
              </div>
              {/* title */}
              <h2 className="text-lg font-bold text-white leading-tight truncate">
                {finding?.name || finding?.type || 'Vulnerability'}
              </h2>
              {/* file + line */}
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <FileCode2 size={11} className="flex-shrink-0" />
                <span className="font-mono truncate">{fileName}{lineNo ? `:${lineNo}` : ''}</span>
              </div>
              {/* severity badge */}
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold ${sevCfg.badge}`}>
                  <SevIcon size={11} />
                  {sev}
                </span>
                {explainData?.source_mode === 'rag' && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-[10px] text-cyan-400">
                    <ExternalLink size={9} /> RAG grounded
                  </span>
                )}
              </div>
            </div>
            {/* close */}
            <button type="button" onClick={onClose}
              className="flex-shrink-0 p-2 rounded-xl text-slate-600 hover:text-white hover:bg-white/[0.06] transition mt-0.5">
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* ── TABS ── */}
        <div className="flex-shrink-0 flex items-center gap-1 px-6 py-3 border-b border-white/[0.05] bg-[#060c18]/80">
          {[
            { id: 'explain', label: 'Explain' },
            { id: 'fix',     label: 'Suggest Fix' },
          ].map(({ id, label }) => (
            <button key={id} type="button" onClick={() => setActiveTab(id)}
              className={`relative px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === id
                  ? 'text-white bg-cyan-500/10 border border-cyan-500/25 shadow-[0_0_14px_rgba(6,182,212,0.12)]'
                  : 'text-slate-500 hover:text-slate-300 border border-transparent hover:border-white/[0.08]'
              }`}>
              {label}
              {activeTab === id && (
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-px h-0.5 w-5 rounded-full bg-cyan-400" />
              )}
            </button>
          ))}
        </div>

        {/* ── SCROLLABLE CONTENT ── */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-3
          scrollbar-thin scrollbar-track-transparent scrollbar-thumb-white/10">
          {activeTab === 'explain' ? renderExplain() : renderFix()}
        </div>

      </div>
    </div>
  );
};

export default AIInsightsDrawer;
