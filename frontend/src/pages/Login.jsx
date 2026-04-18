import React, { useState } from 'react';
import { EyeIcon, EyeSlashIcon, ShieldCheckIcon, QrCodeIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

// step: 'credentials' | 'register_qr' | 'register_otp' | 'login_otp'

const Login = () => {
  const navigate = useNavigate();
  const { login, register, verifyRegistration, verifyLoginMfa } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [step, setStep] = useState('credentials');
  const [challengeToken, setChallengeToken] = useState('');
  const [qrData, setQrData] = useState(null); // { qr_code_base64, otpauth_url, backup_codes }
  const [error, setError] = useState('');

  const resetToCredentials = () => {
    setStep('credentials');
    setOtp('');
    setChallengeToken('');
    setQrData(null);
    setError('');
  };

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'login') {
        const res = await login(email, password);
        if (res?.mfa_required) {
          setChallengeToken(res.challenge_token);
          setStep('login_otp');
          return;
        }
        navigate('/app');
      } else {
        // register — returns QR challenge
        const res = await register(email, password);
        setChallengeToken(res.challenge_token);
        setQrData({
          qr_code_base64: res.qr_code_base64,
          otpauth_url: res.otpauth_url,
          backup_codes: res.backup_codes,
        });
        setStep('register_qr');
      }
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to authenticate. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await verifyRegistration(challengeToken, otp);
      navigate('/app');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Invalid or expired code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await verifyLoginMfa(challengeToken, otp);
      navigate('/app');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Invalid or expired code.');
    } finally {
      setLoading(false);
    }
  };

  const pageTitle = () => {
    if (step === 'register_qr') return 'Set up authenticator';
    if (step === 'register_otp') return 'Verify your authenticator';
    if (step === 'login_otp') return 'Multi-factor verification';
    return mode === 'login' ? 'Login' : 'Create an account';
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8 relative overflow-hidden bg-navy">
      <div className="absolute inset-0 bg-mesh opacity-60" />
      <div className="absolute inset-0 bg-grid-pattern" />
      <div className="max-w-5xl w-full relative grid lg:grid-cols-2 gap-8 items-center">

        {/* Left branding */}
        <div className="space-y-6 text-slate-200">
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-white/5 border border-white/10">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-cyber to-accent flex items-center justify-center shadow-glow">
              <EyeIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-slate-400">Welcome to</p>
              <p className="text-lg font-semibold text-white">DristiScan Security Cloud</p>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white leading-tight">
            Secure your code with <span className="text-accent">real-time</span> vulnerability intelligence.
          </h1>
          <p className="text-slate-400 max-w-xl">
            Paste or upload code, run deep SAST + secret scans, and ship with confidence. Built for modern engineering teams.
          </p>
          <div className="flex gap-4">
            <div className="glass rounded-xl p-4 border border-border">
              <p className="text-sm text-slate-400">Severity-aware</p>
              <p className="text-lg font-semibold text-white">Critical → Low</p>
            </div>
            <div className="glass rounded-xl p-4 border border-border">
              <p className="text-sm text-slate-400">Instant reports</p>
              <p className="text-lg font-semibold text-white">PDF + JSON</p>
            </div>
          </div>
        </div>

        {/* Right form card */}
        <div className="glass-strong rounded-3xl border border-border shadow-2xl p-8 space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-xl font-semibold text-white">{pageTitle()}</p>
            {step === 'credentials' && (
              <button
                onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
                className="text-sm text-accent hover:underline"
                type="button"
              >
                {mode === 'login' ? 'Need an account?' : 'Have an account?'}
              </button>
            )}
            {(step === 'login_otp' || step === 'register_otp') && (
              <button onClick={resetToCredentials} className="text-sm text-accent hover:underline" type="button">
                Back
              </button>
            )}
          </div>

          {error && (
            <p className="text-sm text-red-300 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">{error}</p>
          )}

          {/* ── CREDENTIALS STEP ── */}
          {step === 'credentials' && (
            <form className="space-y-4" onSubmit={handleCredentialsSubmit}>
              <div className="space-y-2">
                <label className="text-sm text-slate-300">Email</label>
                <input
                  required type="email" value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent"
                  placeholder="you@company.com"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm text-slate-300">Password</label>
                <div className="relative">
                  <input
                    required type={show ? 'text' : 'password'} value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-surface border border-border rounded-xl px-4 py-3 pr-11 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent"
                    placeholder="••••••••"
                  />
                  <button type="button" onClick={() => setShow(!show)} className="absolute right-3 top-3 text-slate-400">
                    {show ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                  </button>
                </div>
              </div>
              <button
                type="submit" disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyber to-accent text-white font-semibold shadow-glow hover:opacity-95 transition"
              >
                {loading ? 'Processing...' : mode === 'login' ? 'Login Securely' : 'Continue'}
              </button>
            </form>
          )}

          {/* ── REGISTER QR STEP ── */}
          {step === 'register_qr' && qrData && (
            <div className="space-y-5">
              <div className="flex items-start gap-3 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                <ShieldCheckIcon className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">
                  MFA is required for all accounts. Scan this QR code with <strong className="text-white">Google Authenticator</strong>, <strong className="text-white">Authy</strong>, or any TOTP app.
                </p>
              </div>
              <div className="flex justify-center">
                <div className="rounded-2xl border border-white/10 bg-white p-3">
                  <img src={qrData.qr_code_base64} alt="MFA QR code" className="w-48 h-48 object-contain" />
                </div>
              </div>
              {qrData.backup_codes?.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-slate-400 uppercase tracking-wide">
                    Backup codes — save these securely, they won't be shown again
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {qrData.backup_codes.map((code) => (
                      <span key={code} className="text-sm font-mono text-slate-200 px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08]">
                        {code}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <button
                type="button"
                onClick={() => { setStep('register_otp'); setError(''); }}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold transition hover:opacity-95"
              >
                I've scanned the QR — Continue
              </button>
            </div>
          )}

          {/* ── REGISTER OTP VERIFY STEP ── */}
          {step === 'register_otp' && (
            <form className="space-y-4" onSubmit={handleRegisterOtp}>
              <div className="flex items-start gap-3 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                <QrCodeIcon className="h-5 w-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-slate-300">
                  Enter the 6-digit code from your authenticator app to complete account setup.
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm text-slate-300">One-time passcode</label>
                <input
                  autoFocus required inputMode="numeric" pattern="[0-9]*"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent tracking-widest font-mono text-center text-xl"
                  placeholder="123456"
                />
              </div>
              <button
                type="submit" disabled={loading || otp.length < 6}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-semibold transition hover:opacity-95 disabled:opacity-60"
              >
                {loading ? 'Verifying...' : 'Verify & activate account'}
              </button>
              <button type="button" onClick={() => setStep('register_qr')} className="w-full text-sm text-slate-500 hover:text-slate-300 transition">
                ← Back to QR code
              </button>
            </form>
          )}

          {/* ── LOGIN OTP STEP ── */}
          {step === 'login_otp' && (
            <form className="space-y-4" onSubmit={handleLoginOtp}>
              <p className="text-sm text-slate-300">
                Enter the 6-digit code from your authenticator app to finish signing in.
              </p>
              <div className="space-y-2">
                <label className="text-sm text-slate-300">One-time passcode</label>
                <input
                  autoFocus required inputMode="numeric" pattern="[0-9]*"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent tracking-widest font-mono text-center text-xl"
                  placeholder="123456"
                />
              </div>
              <button
                type="submit" disabled={loading || !otp}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyber to-accent text-white font-semibold shadow-glow hover:opacity-95 transition disabled:opacity-60"
              >
                {loading ? 'Verifying...' : 'Verify & continue'}
              </button>
            </form>
          )}

          <p className="text-xs text-slate-500 text-center">
            By signing in you agree to security monitoring and scanning policies.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
