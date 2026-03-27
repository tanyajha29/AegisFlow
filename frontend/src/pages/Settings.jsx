import React, { useState } from 'react';
import { UserCircleIcon, KeyIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import GlassCard from '../components/GlassCard.jsx';

const Toggle = ({ label, description, enabled, onToggle }) => (
  <div className="flex items-center justify-between py-3">
    <div>
      <p className="text-sm font-medium text-slate-200">{label}</p>
      {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
    </div>
    <button
      onClick={onToggle}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-accent' : 'bg-slate-700'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform bg-white rounded-full shadow transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  </div>
);

const SectionHeader = ({ icon: Icon, title, description }) => (
  <div className="flex items-start gap-3 mb-5">
    <div className="h-9 w-9 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center flex-shrink-0">
      <Icon className="h-5 w-5 text-accent" />
    </div>
    <div>
      <h2 className="text-sm font-semibold text-white">{title}</h2>
      {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
    </div>
  </div>
);

const Settings = () => {
  const [dark, setDark] = useState(true);
  const [alerts, setAlerts] = useState(true);
  const [apiKey] = useState('sk_live_2f8d****c5d');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <div className="space-y-8 max-w-3xl">
      {/* Page header */}
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-widest text-slate-500">Settings</p>
        <h1 className="text-2xl font-bold text-white">Workspace preferences</h1>
        <p className="text-sm text-slate-500">Manage profile, API keys, and theme.</p>
      </div>

      {/* Profile */}
      <GlassCard className="p-6">
        <SectionHeader
          icon={UserCircleIcon}
          title="Profile"
          description="Update your display name and email address."
        />
        <div className="grid sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs text-slate-500 uppercase tracking-wide">Full name</label>
            <input
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-3 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-accent/40 transition"
              defaultValue="Jane Doe"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs text-slate-500 uppercase tracking-wide">Email</label>
            <input
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-3 py-2.5 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-accent/40 transition"
              defaultValue="jane@codeshield.io"
            />
          </div>
        </div>
        <div className="mt-4">
          <button className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 text-white text-sm font-semibold shadow-[0_0_12px_rgba(34,211,238,0.25)] hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition">
            Save profile
          </button>
        </div>
      </GlassCard>

      {/* API Key */}
      <GlassCard className="p-6">
        <SectionHeader
          icon={KeyIcon}
          title="API Key Management"
          description="Use this key to authenticate API requests."
        />
        <div className="flex items-center gap-2 bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3">
          <span className="flex-1 text-sm font-mono text-slate-300">{apiKey}</span>
          <button
            onClick={handleCopy}
            className="text-xs text-accent hover:text-white transition font-medium"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div className="mt-3">
          <button className="px-4 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-slate-300 text-sm hover:bg-white/[0.08] transition">
            Generate new key
          </button>
        </div>
      </GlassCard>

      {/* Preferences */}
      <GlassCard className="p-6">
        <SectionHeader
          icon={AdjustmentsHorizontalIcon}
          title="Preferences"
          description="Customize your workspace experience."
        />
        <div className="divide-y divide-white/[0.06]">
          <Toggle
            label="Dark theme"
            description="Use the dark color scheme across the app."
            enabled={dark}
            onToggle={() => setDark(!dark)}
          />
          <Toggle
            label="Alert notifications"
            description="Receive alerts when critical vulnerabilities are found."
            enabled={alerts}
            onToggle={() => setAlerts(!alerts)}
          />
        </div>
      </GlassCard>
    </div>
  );
};

export default Settings;
