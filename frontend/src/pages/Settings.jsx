import React, { useState } from 'react';
import { UserCircleIcon, KeyIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import GlassCard from '../components/GlassCard.jsx';
import { useAuth } from '../context/AuthContext.jsx';

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
  const { user, startMfaSetup, verifyMfa, disableMfa } = useAuth();
  const [dark, setDark] = useState(true);
  const [alerts, setAlerts] = useState(true);
  const [apiKey] = useState('sk_live_2f8d****c5d');
  const [copied, setCopied] = useState(false);
  const [mfaSetup, setMfaSetup] = useState(null);
  const [mfaOtp, setMfaOtp] = useState('');
  const [disableOtp, setDisableOtp] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [statusMsg, setStatusMsg] = useState('');
  const [error, setError] = useState('');

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  const beginMfaSetup = async () => {
    setError('');
    setStatusMsg('');
    try {
      const data = await startMfaSetup();
      setMfaSetup(data);
      setBackupCodes(data.backup_codes || []);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not start MFA setup.');
    }
  };

  const confirmMfaSetup = async () => {
    setError('');
    setStatusMsg('');
    try {
      await verifyMfa(mfaOtp);
      setStatusMsg('Multi-factor authentication is now enabled.');
      setMfaSetup(null);
      setMfaOtp('');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Verification failed. Please try again.');
    }
  };

  const handleDisableMfa = async () => {
    setError('');
    setStatusMsg('');
    try {
      await disableMfa(disableOtp);
      setStatusMsg('MFA disabled for this account.');
      setDisableOtp('');
      setMfaSetup(null);
      setBackupCodes([]);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not disable MFA.');
    }
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

      {/* MFA */}
      <GlassCard className="p-6">
        <SectionHeader
          icon={KeyIcon}
          title="Multi-factor Authentication"
          description="Protect account access with an authenticator app."
        />
        <div className="flex items-center gap-2 mb-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              user?.mfa_enabled ? 'bg-green-500/15 text-green-300 border border-green-500/30' : 'bg-slate-800/80 text-slate-300 border border-slate-700/60'
            }`}
          >
            {user?.mfa_enabled ? 'Enabled' : 'Disabled'}
          </span>
          {statusMsg && <span className="text-xs text-green-300">{statusMsg}</span>}
          {error && <span className="text-xs text-red-300">{error}</span>}
        </div>

        {!user?.mfa_enabled && (
          <div className="space-y-4">
            <p className="text-sm text-slate-300">
              Scan a QR code with Google Authenticator, Microsoft Authenticator, or Authy, then confirm with the 6-digit code.
            </p>
            {!mfaSetup ? (
              <button
                onClick={beginMfaSetup}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 text-white text-sm font-semibold shadow-[0_0_12px_rgba(34,211,238,0.25)] hover:shadow-[0_0_20px_rgba(34,211,238,0.4)] transition"
              >
                Start MFA setup
              </button>
            ) : (
              <div className="grid md:grid-cols-2 gap-5">
                <div className="space-y-3">
                  <p className="text-xs text-slate-400 uppercase tracking-wide">Scan QR</p>
                  <div className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4 flex items-center justify-center">
                    <img src={mfaSetup.qr_code_base64} alt="MFA QR code" className="w-48 h-48 object-contain" />
                  </div>
                  <p className="text-[11px] text-slate-500 break-all bg-white/[0.03] border border-white/[0.06] rounded-xl p-2">
                    {mfaSetup.otpauth_url}
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm text-slate-300">Enter 6-digit code</label>
                    <input
                      value={mfaOtp}
                      onChange={(e) => setMfaOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      inputMode="numeric"
                      pattern="[0-9]*"
                      className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent tracking-widest font-mono"
                      placeholder="123456"
                    />
                  </div>
                  {!!backupCodes.length && (
                    <div>
                      <p className="text-xs text-slate-400 uppercase tracking-wide mb-2">Backup codes (save securely)</p>
                      <div className="grid grid-cols-2 gap-2">
                        {backupCodes.map((code) => (
                          <span key={code} className="text-sm font-mono text-slate-200 px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                            {code}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <button
                    onClick={confirmMfaSetup}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold shadow-[0_0_12px_rgba(16,185,129,0.25)] hover:shadow-[0_0_18px_rgba(16,185,129,0.35)] transition"
                    disabled={!mfaOtp}
                    type="button"
                  >
                    Verify & enable MFA
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {user?.mfa_enabled && (
          <div className="space-y-3">
            <p className="text-sm text-slate-300">
              MFA is active. Use your authenticator app at login. Enter a fresh code below to disable if needed.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                value={disableOtp}
                onChange={(e) => setDisableOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                inputMode="numeric"
                pattern="[0-9]*"
                className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent tracking-widest font-mono"
                placeholder="Enter OTP to disable"
              />
              <button
                onClick={handleDisableMfa}
                type="button"
                className="px-5 py-3 rounded-xl bg-white/[0.06] border border-white/[0.12] text-sm text-white hover:bg-white/[0.1] transition"
                disabled={!disableOtp}
              >
                Disable MFA
              </button>
            </div>
          </div>
        )}
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
