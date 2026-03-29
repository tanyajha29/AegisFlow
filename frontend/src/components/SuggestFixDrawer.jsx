import React, { useState } from 'react';
import { XMarkIcon, ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';

const Section = ({ label, children }) => (
  <div className="space-y-2">
    <p className="text-xs uppercase tracking-widest text-blue-400/80 font-semibold">{label}</p>
    <div className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">{children || 'Not provided.'}</div>
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
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-40">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="absolute right-0 top-0 h-full w-full max-w-2xl bg-gradient-to-b from-slate-900/98 to-slate-950/98 border-l border-blue-500/20 shadow-[0_0_40px_rgba(59,130,246,0.2)]"
          >
            {/* Sticky Header */}
            <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 border-b border-blue-500/15 bg-slate-900/80 backdrop-blur-xl">
              <div className="space-y-1">
                <p className="text-xs uppercase tracking-widest text-blue-400/70 font-semibold">AI Fix Suggestion</p>
                <p className="text-lg font-bold text-white">
                  {fixData?.title || 'Suggested Fix'}
                </p>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-blue-500/10 transition-all"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Scrollable Content */}
            <div className="h-[calc(100%-80px)] overflow-y-auto px-6 py-6 space-y-6 scrollbar-thin scrollbar-thumb-blue-500/20 scrollbar-track-transparent">
              {loading && (
                <div className="space-y-4">
                  {[...Array(5)].map((_, idx) => (
                    <div key={idx} className="space-y-2">
                      <div className="h-4 w-24 rounded-lg bg-blue-500/10 animate-pulse" />
                      <div className="h-12 w-full rounded-lg bg-blue-500/5 animate-pulse" />
                    </div>
                  ))}
                </div>
              )}

              {!loading && error && (
                <div className="p-4 rounded-lg border border-red-500/30 bg-red-500/5 text-red-200 text-sm space-y-2">
                  <p className="font-semibold">Error generating fix</p>
                  <p>{error}</p>
                </div>
              )}

              {!loading && !error && fixData && (
                <div className="space-y-6">
                  <Section label="Fix Summary">{fixData.fix_summary}</Section>
                  <Section label="Why This Fix Is Safer">{fixData.why_this_fix_is_safer}</Section>

                  <div className="space-y-3">
                    <p className="text-xs uppercase tracking-widest text-blue-400/80 font-semibold">Fixed Code</p>
                    <div className="relative group">
                      <pre className="bg-slate-800/40 border border-blue-500/15 rounded-lg p-4 text-xs text-slate-100 whitespace-pre-wrap font-mono overflow-x-auto leading-relaxed">
                        {fixData.fixed_code || 'A detailed code fix is not currently available for this finding.'}
                      </pre>
                      {fixData.fixed_code && (
                        <motion.button
                          type="button"
                          onClick={handleCopy}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="absolute top-3 right-3 inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-500/20 text-xs text-slate-200 border border-blue-500/30 hover:bg-blue-500/30 hover:border-blue-500/50 transition-all"
                        >
                          {copied ? <CheckIcon className="h-4 w-4 text-green-400" /> : <ClipboardIcon className="h-4 w-4" />}
                          {copied ? 'Copied!' : 'Copy'}
                        </motion.button>
                      )}
                    </div>
                  </div>

                  {fixData.notes?.length > 0 && (
                    <div className="space-y-3">
                      <p className="text-xs uppercase tracking-widest text-blue-400/80 font-semibold">Notes</p>
                      <ul className="space-y-2">
                        {fixData.notes.map((n, idx) => (
                          <li key={idx} className="flex gap-3 text-sm text-slate-200">
                            <span className="text-blue-400 font-bold flex-shrink-0 mt-0.5">•</span>
                            <span>{n}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {fixData.references?.length > 0 && (
                    <div className="space-y-3">
                      <p className="text-xs uppercase tracking-widest text-blue-400/80 font-semibold">References</p>
                      <div className="flex flex-wrap gap-2">
                        {fixData.references.map((ref, idx) => (
                          <span
                            key={`${ref.label}-${idx}`}
                            className="px-3 py-2 rounded-lg bg-blue-500/10 text-xs text-slate-200 border border-blue-500/20 hover:border-blue-500/40 transition-all"
                          >
                            {ref.label} · {ref.source}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {!loading && !error && !fixData && (
                <p className="text-sm text-slate-400 text-center py-8">
                  A detailed code fix is not currently available for this finding.
                </p>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default SuggestFixDrawer;
