import React, { useEffect, useMemo, useState } from 'react';
import { XMarkIcon, ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';
import { explainVulnerability, suggestFix } from '../../lib/rag.js';
import CodeInsightPreview from './CodeInsightPreview.jsx';
import FindingBadgeList from './FindingBadgeList.jsx';
import InsightSectionCard from './InsightSectionCard.jsx';

const TabButton = ({ active, children, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className={`px-3 py-2 rounded-lg text-sm font-medium transition border ${
      active
        ? 'bg-white/10 border-white/20 text-white shadow'
        : 'bg-transparent border-transparent text-slate-400 hover:text-white hover:border-white/10'
    }`}
  >
    {children}
  </button>
);

const LoadingSkeleton = () => (
  <div className="space-y-3">
    {[...Array(6)].map((_, idx) => (
      <div key={idx} className="h-10 rounded-lg bg-white/5 animate-pulse" />
    ))}
  </div>
);

const ErrorBlock = ({ message, onRetry }) => (
  <div className="p-3 rounded-lg border border-red-500/40 bg-red-500/10 text-red-100 text-sm space-y-2">
    <p>Could not generate AI insights right now. {message}</p>
    {onRetry && (
      <button
        type="button"
        onClick={onRetry}
        className="px-3 py-1 rounded-md bg-white/10 border border-white/10 text-xs text-white hover:bg-white/15"
      >
        Retry
      </button>
    )}
  </div>
);

const References = ({ items }) => (
  <InsightSectionCard title="References">
    {items?.length ? (
      <div className="flex flex-wrap gap-2">
        {items.map((ref, idx) => (
          <span
            key={`${ref.label}-${idx}`}
            className="px-2 py-1 rounded-full bg-white/10 text-xs text-slate-100 border border-white/10"
          >
            {ref.label} · {ref.source}
          </span>
        ))}
      </div>
    ) : (
      'No references provided.'
    )}
  </InsightSectionCard>
);

const AIInsightsDrawer = ({ isOpen, onClose, finding, initialTab = 'explain' }) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [explainData, setExplainData] = useState(null);
  const [fixData, setFixData] = useState(null);
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [loadingFix, setLoadingFix] = useState(false);
  const [errorExplain, setErrorExplain] = useState(null);
  const [errorFix, setErrorFix] = useState(null);
  const [copiedFixed, setCopiedFixed] = useState(false);

  useEffect(() => setActiveTab(initialTab), [initialTab, isOpen]);

  useEffect(() => {
    setExplainData(null);
    setFixData(null);
    setErrorExplain(null);
    setErrorFix(null);
    setLoadingExplain(false);
    setLoadingFix(false);
    setCopiedFixed(false);
  }, [finding]);

  const severityBadge = useMemo(() => {
    const sev = finding?.severity || 'Medium';
    const map = {
      Critical: 'text-critical border-critical/60 bg-critical/10',
      High: 'text-high border-high/60 bg-high/10',
      Medium: 'text-medium border-medium/60 bg-medium/10',
      Low: 'text-low border-low/60 bg-low/10',
    };
    return map[sev] || map.Medium;
  }, [finding]);

  const runExplain = async () => {
    if (!finding || explainData || loadingExplain) return;
    setLoadingExplain(true);
    setErrorExplain(null);
    try {
      setExplainData(await explainVulnerability(finding));
    } catch (err) {
      setErrorExplain(err.response?.data?.detail || err.message || 'Unknown error');
    } finally {
      setLoadingExplain(false);
    }
  };

  const runFix = async () => {
    if (!finding || fixData || loadingFix) return;
    setLoadingFix(true);
    setErrorFix(null);
    try {
      setFixData(await suggestFix(finding));
    } catch (err) {
      setErrorFix(err.response?.data?.detail || err.message || 'Unknown error');
    } finally {
      setLoadingFix(false);
    }
  };

  useEffect(() => {
    if (!isOpen) return;
    if (activeTab === 'explain') runExplain();
    if (activeTab === 'fix') runFix();
  }, [activeTab, isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleCopyFixed = () => {
    if (!fixData?.fixed_code) return;
    navigator.clipboard.writeText(fixData.fixed_code).then(
      () => {
        setCopiedFixed(true);
        setTimeout(() => setCopiedFixed(false), 1500);
      },
      () => setCopiedFixed(false),
    );
  };

  const renderExplain = () => {
    if (loadingExplain) return <LoadingSkeleton />;
    if (errorExplain) return <ErrorBlock message={errorExplain} onRetry={runExplain} />;
    if (!explainData) return <p className="text-sm text-slate-400">No explanation available.</p>;
    return (
      <div className="space-y-4">
        <CodeInsightPreview
          code={finding?.code_snippet || finding?.code || 'No code provided.'}
          lineNumber={finding?.line_number || finding?.line || null}
          variant="vulnerable"
          title={finding?.file_name || finding?.file || 'Target'}
        />
        <FindingBadgeList
          items={[
            { label: explainData.title || finding?.type || 'Finding', severity: finding?.severity || 'Medium' },
          ]}
        />
        <div className="grid gap-3">
          <InsightSectionCard title="Summary">{explainData.summary}</InsightSectionCard>
          <InsightSectionCard title="Technical Explanation">{explainData.technical_explanation}</InsightSectionCard>
          <InsightSectionCard title="Impact">{explainData.impact}</InsightSectionCard>
          <InsightSectionCard title="Exploit Scenario">{explainData.exploit_scenario}</InsightSectionCard>
          <InsightSectionCard title="Recommendation">{explainData.fix_recommendation}</InsightSectionCard>
          <InsightSectionCard title="Secure Example">
            <pre className="bg-slate-800/80 border border-white/5 rounded-lg p-3 text-xs text-slate-100 whitespace-pre-wrap">
              {explainData.secure_example || 'No example provided.'}
            </pre>
          </InsightSectionCard>
          {explainData.retrieved_context_count !== undefined && (
            <InsightSectionCard title="Grounding">
              Grounded using {explainData.retrieved_context_count} knowledge source
              {explainData.retrieved_context_count === 1 ? '' : 's'}.
            </InsightSectionCard>
          )}
          <References items={explainData.references} />
        </div>
      </div>
    );
  };

  const renderFix = () => {
    if (loadingFix) return <LoadingSkeleton />;
    if (errorFix) return <ErrorBlock message={errorFix} onRetry={runFix} />;
    if (!fixData) return <p className="text-sm text-slate-400">No fix suggestion available.</p>;
    return (
      <div className="space-y-4">
        <div className="grid gap-3">
          <CodeInsightPreview
            code={finding?.code_snippet || finding?.code || 'No code provided.'}
            lineNumber={finding?.line_number || finding?.line || null}
            variant="vulnerable"
            title="Vulnerable Code"
          />
          <CodeInsightPreview
            code={fixData.fixed_code || 'No fixed code provided.'}
            lineNumber={finding?.line_number || finding?.line || null}
            variant="fixed"
            title="Secure Fix"
          />
        </div>
        <FindingBadgeList
          items={[
            { label: fixData.title || finding?.type || 'Fix Suggestion', severity: finding?.severity || 'Medium' },
          ]}
        />
        <div className="grid gap-3">
          <InsightSectionCard title="Fix Summary">{fixData.fix_summary}</InsightSectionCard>
          <InsightSectionCard title="Why This Fix Is Safer">{fixData.why_this_fix_is_safer}</InsightSectionCard>
          <InsightSectionCard title="Notes">
            {fixData.notes?.length ? (
              <ul className="list-disc list-inside text-sm text-slate-200 space-y-1">
                {fixData.notes.map((n, idx) => (
                  <li key={idx}>{n}</li>
                ))}
              </ul>
            ) : (
              'No additional notes provided.'
            )}
          </InsightSectionCard>
          <InsightSectionCard title="Copy Fixed Code">
            <div className="flex items-center justify-between bg-slate-800/60 border border-white/5 rounded-lg p-3">
              <span className="text-xs text-slate-200">Secure snippet</span>
              <button
                type="button"
                onClick={handleCopyFixed}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-white/10 text-xs text-slate-100 border border-white/10 hover:bg-white/15"
              >
                {copiedFixed ? <CheckIcon className="h-4 w-4" /> : <ClipboardIcon className="h-4 w-4" />}
                {copiedFixed ? 'Copied' : 'Copy'}
              </button>
            </div>
          </InsightSectionCard>
          <References items={fixData.references} />
        </div>
      </div>
    );
  };

  return (
    <div className={`fixed inset-0 z-40 ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`} aria-hidden={!isOpen}>
      <div
        className={`absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity ${isOpen ? 'opacity-100' : 'opacity-0'}`}
        onClick={onClose}
      />
      <div
        className={`absolute right-0 top-0 h-full w-full max-w-3xl bg-slate-950/95 border-l border-cyan-400/20 shadow-[0_0_50px_rgba(0,255,255,0.12)] transform transition-all ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/5 bg-slate-950/60 backdrop-blur">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">AI Insights</p>
            <p className="text-lg font-semibold text-white">{finding?.name || finding?.type || 'Vulnerability'}</p>
            <p className="text-xs text-slate-400">
              {finding?.file_name || finding?.file || 'Unknown file'}
              {finding?.line_number ? ` · line ${finding.line_number}` : ''}
            </p>
            <span className={`inline-flex mt-2 px-2 py-1 rounded-md text-xs border ${severityBadge}`}>
              {finding?.severity || 'Medium'}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="px-5 py-3 border-b border-white/5 flex items-center gap-2">
          <TabButton active={activeTab === 'explain'} onClick={() => setActiveTab('explain')}>
            Explain
          </TabButton>
          <TabButton active={activeTab === 'fix'} onClick={() => setActiveTab('fix')}>
            Suggest Fix
          </TabButton>
        </div>

        <div className="h-[calc(100%-140px)] overflow-y-auto p-5 space-y-4">
          {activeTab === 'explain' ? renderExplain() : renderFix()}
        </div>
      </div>
    </div>
  );
};

export default AIInsightsDrawer;
