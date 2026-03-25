import React, { useState } from 'react';
import { XMarkIcon, ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';

const Section = ({ label, children }) => (
  <div className="space-y-1">
    <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
    <div className="text-sm text-slate-100 whitespace-pre-wrap">{children || 'Not provided.'}</div>
  </div>
);

const SuggestFixDrawer = ({ open, onClose, loading, error, fixData }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!fixData?.fixed_code) return;
    try {
      await navigator.clipboard.writeText(fixData.fixed_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (e) {
      setCopied(false);
    }
  };

  return (
    <div className={`fixed inset-0 z-40 ${open ? 'pointer-events-auto' : 'pointer-events-none'}`} aria-hidden={!open}>
      <div
        className={`absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity ${
          open ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={onClose}
      />
      <div
        className={`absolute right-0 top-0 h-full w-full max-w-xl bg-slate-900/95 border-l border-white/10 shadow-2xl transform transition-all ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">AI Fix Suggestion</p>
            <p className="text-lg font-semibold text-white">
              {fixData?.title || 'Suggested Fix'}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/10"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="h-[calc(100%-60px)] overflow-y-auto p-5 space-y-4">
          {loading && (
            <div className="space-y-3">
              {[...Array(6)].map((_, idx) => (
                <div key={idx} className="h-10 rounded-lg bg-white/5 animate-pulse" />
              ))}
            </div>
          )}

          {!loading && error && (
            <div className="p-3 rounded-lg border border-red-500/40 bg-red-500/10 text-red-100 text-sm">
              Could not generate a fix suggestion right now. {error}
            </div>
          )}

          {!loading && !error && fixData && (
            <div className="space-y-4">
              <Section label="Fix Summary">{fixData.fix_summary}</Section>
              <Section label="Why This Fix Is Safer">{fixData.why_this_fix_is_safer}</Section>
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-wide text-slate-400">Fixed Code</p>
                <div className="relative">
                  <pre className="bg-slate-800/80 border border-white/5 rounded-lg p-3 text-xs text-slate-100 whitespace-pre-wrap">
                    {fixData.fixed_code || 'A detailed code fix is not currently available for this finding.'}
                  </pre>
                  {fixData.fixed_code && (
                    <button
                      type="button"
                      onClick={handleCopy}
                      className="absolute top-2 right-2 inline-flex items-center gap-1 px-2 py-1 rounded-md bg-white/10 text-xs text-slate-100 border border-white/10 hover:bg-white/15"
                    >
                      {copied ? <CheckIcon className="h-4 w-4" /> : <ClipboardIcon className="h-4 w-4" />}
                      {copied ? 'Copied' : 'Copy'}
                    </button>
                  )}
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-wide text-slate-400">Notes</p>
                {fixData.notes?.length ? (
                  <ul className="list-disc list-inside text-sm text-slate-200 space-y-1">
                    {fixData.notes.map((n, idx) => (
                      <li key={idx}>{n}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-400">No additional notes provided.</p>
                )}
              </div>
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-wide text-slate-400">References</p>
                {fixData.references?.length ? (
                  <div className="flex flex-wrap gap-2">
                    {fixData.references.map((ref, idx) => (
                      <span
                        key={`${ref.label}-${idx}`}
                        className="px-2 py-1 rounded-full bg-white/10 text-xs text-slate-100 border border-white/10"
                      >
                        {ref.label} · {ref.source}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No references provided.</p>
                )}
              </div>
            </div>
          )}

          {!loading && !error && !fixData && (
            <p className="text-sm text-slate-400">
              A detailed code fix is not currently available for this finding.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SuggestFixDrawer;
