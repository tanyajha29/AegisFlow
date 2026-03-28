import React, { useState } from 'react';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

const Login = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('login');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password);
      }
      navigate('/app');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8 relative overflow-hidden bg-navy">
      <div className="absolute inset-0 bg-mesh opacity-60" />
      <div className="absolute inset-0 bg-grid-pattern" />
      <div className="max-w-5xl w-full relative grid lg:grid-cols-2 gap-8 items-center">
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

        <div className="glass-strong rounded-3xl border border-border shadow-2xl p-8 space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-xl font-semibold text-white">{mode === 'login' ? 'Login' : 'Create an account'}</p>
            <button
              onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
              className="text-sm text-accent hover:underline"
            >
              {mode === 'login' ? 'Need an account?' : 'Have an account?'}
            </button>
          </div>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Email</label>
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent"
                placeholder="you@company.com"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Password</label>
              <div className="relative">
                <input
                  required
                  type={show ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 pr-11 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-accent"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShow(!show)}
                  className="absolute right-3 top-3 text-slate-400"
                >
                  {show ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-cyber to-accent text-white font-semibold shadow-glow hover:opacity-95 transition"
            >
              {loading ? 'Processing...' : mode === 'login' ? 'Login Securely' : 'Create Account'}
            </button>
          </form>
          <p className="text-xs text-slate-500 text-center">
            By signing in you agree to security monitoring and scanning policies.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

