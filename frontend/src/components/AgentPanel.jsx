import React from 'react';
import { motion } from 'framer-motion';
import { Shield, KeyRound, Lock, Package, FileText, Loader2 } from 'lucide-react';

const agentConfig = [
  { label: 'Injection Agent', icon: Shield },
  { label: 'Secrets Agent', icon: KeyRound },
  { label: 'Auth Agent', icon: Lock },
  { label: 'Dependency Agent', icon: Package },
  { label: 'Report Agent', icon: FileText },
];

const statusBadge = (state) => {
  if (state === 'running') {
    return (
      <span className="px-2 py-0.5 text-[11px] rounded-full bg-accent/20 text-accent border border-accent/40">
        Running
      </span>
    );
  }
  if (state === 'active') {
    return (
      <span className="px-2 py-0.5 text-[11px] rounded-full bg-green-500/15 text-green-300 border border-green-500/30">
        Active
      </span>
    );
  }
  return (
    <span className="px-2 py-0.5 text-[11px] rounded-full bg-slate-500/10 text-slate-200 border border-slate-500/30">
      Pending
    </span>
  );
};

const AgentPanel = ({ agentsUsed = [], logs = [], loading = false }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 rounded-xl border border-border bg-card shadow-glow space-y-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">AI Agents</p>
          <h3 className="text-lg font-semibold text-white">Multi-Agent Status</h3>
        </div>
        {loading && <Loader2 className="h-5 w-5 text-accent animate-spin" />}
      </div>

      <div className="grid grid-cols-2 gap-2">
        {agentConfig.map((agent) => {
          const Icon = agent.icon;
          const active = agentsUsed.includes(agent.label);
          const state = loading ? 'running' : active ? 'active' : 'pending';
          return (
            <motion.div
              key={agent.label}
              whileHover={{ scale: 1.01 }}
              className={`flex items-center justify-between px-3 py-2 rounded-lg border ${
                active ? 'border-accent/40 bg-accent/5' : 'border-border bg-white/5'
              }`}
            >
              <div className="flex items-center gap-2 text-slate-100">
                <Icon className={`h-4 w-4 ${active ? 'text-accent' : 'text-slate-400'}`} />
                <span className="text-sm">{agent.label}</span>
              </div>
              {statusBadge(state)}
            </motion.div>
          );
        })}
      </div>

      <div className="rounded-lg border border-border bg-black/40 p-3 h-40 overflow-auto text-sm text-slate-200">
        <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
          <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
          <span>Agent logs</span>
        </div>
        {logs.length === 0 ? (
          <p className="text-slate-500 text-xs">No agent logs returned.</p>
        ) : (
          logs.map((line, idx) => (
            <div key={`${line}-${idx}`} className="font-mono text-[12px] leading-5">
              {line}
            </div>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default AgentPanel;
