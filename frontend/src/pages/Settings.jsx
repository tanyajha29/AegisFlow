import React, { useState } from 'react';
import GlassCard from '../components/GlassCard.jsx';

const Settings = () => {
  const [dark, setDark] = useState(true);
  const [alerts, setAlerts] = useState(true);
  const [apiKey] = useState('sk_live_2f8d****c5d');

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Settings</p>
        <h1 className="text-3xl font-semibold text-white">Workspace preferences</h1>
        <p className="text-slate-500 text-sm">Manage profile, API keys, and theme.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Profile</p>
          <div className="grid grid-cols-2 gap-3">
            <input className="bg-surface border border-border rounded-xl px-3 py-2 text-sm" defaultValue="Jane Doe" />
            <input className="bg-surface border border-border rounded-xl px-3 py-2 text-sm" defaultValue="jane@codeshield.io" />
          </div>
          <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyber to-accent text-white shadow-glow text-sm">
            Save profile
          </button>
        </GlassCard>

        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">API Key Management</p>
          <div className="bg-white/5 border border-border rounded-xl px-3 py-2 flex items-center justify-between">
            <span className="text-sm font-mono">{apiKey}</span>
            <button className="text-xs text-accent">Copy</button>
          </div>
          <button className="px-4 py-2 rounded-xl bg-white/5 border border-border text-slate-200 text-sm">
            Generate new key
          </button>
        </GlassCard>

        <GlassCard className="p-4 space-y-3">
          <p className="text-sm text-slate-400">Preferences</p>
          <Toggle label="Dark theme" enabled={dark} onToggle={() => setDark(!dark)} />
          <Toggle label="Alert notifications" enabled={alerts} onToggle={() => setAlerts(!alerts)} />
        </GlassCard>
      </div>
    </div>
  );
};

const Toggle = ({ label, enabled, onToggle }) => (
  <div className="flex items-center justify-between">
    <span className="text-sm text-slate-200">{label}</span>
    <button
      onClick={onToggle}
      className={`relative inline-flex h-7 w-12 items-center rounded-full transition ${
        enabled ? 'bg-cyber' : 'bg-slate-700'
      }`}
    >
      <span
        className={`inline-block h-5 w-5 transform bg-white rounded-full transition ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  </div>
);

export default Settings;
