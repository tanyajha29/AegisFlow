import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, KeyRound, Lock, Package, FileText, Loader2, ChevronDown } from 'lucide-react';

// Agents the backend actually runs during a scan.
// label must match exactly what scanner/orchestrator.py puts in ai_agents_used.
const ACTIVE_AGENTS = [
  { label: 'Injection Agent', icon: Shield },
  { label: 'Secrets Agent', icon: KeyRound },
];

// Agents that are planned but not yet implemented.
const PLANNED_AGENTS = [
  { label: 'Auth Agent', icon: Lock },
  { label: 'Dependency Agent', icon: Package },
  { label: 'Report Agent', icon: FileText },
];

const StatusBadge = ({ state }) => {
  const styles = {
    running:   'bg-accent/20 text-accent border-accent/40',
    completed: 'bg-green-500/15 text-green-300 border-green-500/30',
    error:     'bg-red-500/15 text-red-300 border-red-500/30',
    planned:   'bg-slate-700/40 text-slate-400 border-slate-600/40',
  };
  const labels = {
    running:   'Running',
    completed: 'Completed',
    error:     'Error',
    planned:   'Planned',
  };
  return (
    <span className={`px-2 py-0.5 text-[11px] rounded-full border ${styles[state] || styles.planned}`}>
      {labels[state] || 'Planned'}
    </span>
  );
};

const AgentRow = ({ label, icon: Icon, state }) => (
  <motion.div
    whileHover={{ scale: 1.01 }}
    className={`flex items-center justify-between px-3 py-2 rounded-lg border ${
      state === 'completed'
        ? 'border-green-500/30 bg-green-500/5'
        : state === 'running'
        ? 'border-accent/40 bg-accent/5'
        : state === 'error'
        ? 'border-red-500/30 bg-red-500/5'
        : 'border-border bg-white/[0.03] opacity-60'
    }`}
  >
    <div className="flex items-center gap-2">
      <Icon
        className={`h-4 w-4 ${
          state === 'completed' ? 'text-green-400'
          : state === 'running' ? 'text-accent'
          : state === 'error' ? 'text-red-400'
          : 'text-slate-600'
        }`}
      />
      <span className={`text-sm ${state === 'planned' ? 'text-slate-500' : 'text-slate-100'}`}>
        {label}
      </span>
    </div>
    <StatusBadge state={state} />
  </motion.div>
);

const AgentPanel = ({ agentsUsed = [], logs = [], loading = false }) => {
  const [logsOpen, setLogsOpen] = useState(true);

  // Derive per-agent state from what the backend reported
  const getState = (label) => {
    if (loading) return 'running';
    if (agentsUsed.includes(label)) return 'completed';
    return 'pending'; // active agent that didn't run this scan (shouldn't normally happen)
  };

  // Only show logs from agents that actually ran
  const activeLogs = logs.filter((line) =>
    ACTIVE_AGENTS.some((a) => line.toLowerCase().includes(a.label.toLowerCase()))
  );

  const completedCount = ACTIVE_AGENTS.filter((a) => agentsUsed.includes(a.label)).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 rounded-xl border border-border bg-card shadow-glow space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">AI Agents</p>
          <h3 className="text-lg font-semibold text-white">Multi-Agent Status</h3>
        </div>
        <div className="flex items-center gap-2">
          {loading && <Loader2 className="h-4 w-4 text-accent animate-spin" />}
          {!loading && (
            <span className="text-xs text-slate-400">
              {completedCount}/{ACTIVE_AGENTS.length} completed
            </span>
          )}
        </div>
      </div>

      {/* Active agents */}
      <div className="space-y-1">
        <p className="text-[11px] uppercase tracking-widest text-slate-500 mb-2">Active</p>
        <div className="grid grid-cols-2 gap-2">
          {ACTIVE_AGENTS.map((agent) => (
            <AgentRow
              key={agent.label}
              label={agent.label}
              icon={agent.icon}
              state={getState(agent.label)}
            />
          ))}
        </div>
      </div>

      {/* Planned agents */}
      <div className="space-y-1">
        <p className="text-[11px] uppercase tracking-widest text-slate-500 mb-2">Coming Soon</p>
        <div className="grid grid-cols-2 gap-2">
          {PLANNED_AGENTS.map((agent) => (
            <AgentRow
              key={agent.label}
              label={agent.label}
              icon={agent.icon}
              state="planned"
            />
          ))}
        </div>
      </div>

      {/* Logs — collapsible, only shows logs from agents that ran */}
      <div className="rounded-lg border border-border bg-black/40 overflow-hidden">
        <button
          type="button"
          onClick={() => setLogsOpen((v) => !v)}
          className="w-full flex items-center justify-between px-3 py-2 text-xs text-slate-400 hover:text-slate-200 transition"
        >
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
            <span>Agent logs {activeLogs.length > 0 ? `(${activeLogs.length})` : ''}</span>
          </div>
          <ChevronDown
            className={`h-3.5 w-3.5 transition-transform ${logsOpen ? 'rotate-180' : ''}`}
          />
        </button>

        <AnimatePresence initial={false}>
          {logsOpen && (
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: 'auto' }}
              exit={{ height: 0 }}
              className="overflow-hidden"
            >
              <div className="px-3 pb-3 h-32 overflow-auto">
                {activeLogs.length === 0 ? (
                  <p className="text-slate-500 text-xs mt-1">No agent logs for this scan.</p>
                ) : (
                  activeLogs.map((line, idx) => (
                    <div key={`${line}-${idx}`} className="font-mono text-[11px] leading-5 text-slate-300">
                      <span className="text-slate-600 mr-2">›</span>
                      {line}
                    </div>
                  ))
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default AgentPanel;
