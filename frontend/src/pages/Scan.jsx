import React, { useState } from 'react';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import CodeEditorPanel from '../components/CodeEditorPanel.jsx';
import ProgressBar from '../components/ProgressBar.jsx';
import SeverityBadge from '../components/SeverityBadge.jsx';
import GlassCard from '../components/GlassCard.jsx';

const Scan = () => {
  const [code, setCode] = useState(`import os\nuser_input = input()\nos.system("ping " + user_input)\n`);
  const [language, setLanguage] = useState('python');
  const [progress, setProgress] = useState(72);

  const findings = [
    { name: 'Command Injection', severity: 'High', file: 'example.py', line: 3 },
    { name: 'Hardcoded secret', severity: 'Medium', file: 'config.js', line: 21 },
    { name: 'Outdated dependency', severity: 'Low', file: 'requirements.txt', line: 5 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan Code</p>
          <h1 className="text-3xl font-semibold text-white">Run a deep security scan</h1>
          <p className="text-slate-500 text-sm">Paste code, upload a file, or trigger via CI.</p>
        </div>
        <button className="hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-border text-slate-200">
          <ArrowPathIcon className="h-5 w-5" />
          Re-run last scan
        </button>
      </div>

      <CodeEditorPanel
        code={code}
        setCode={setCode}
        language={language}
        setLanguage={setLanguage}
        onUpload={() => alert('Upload handler placeholder')}
        onRun={() => setProgress((p) => (p === 100 ? 15 : p + 15))}
      />

      <div className="grid lg:grid-cols-3 gap-4">
        <GlassCard className="p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-slate-400">Scan Progress</p>
            <p className="text-xs text-slate-500">{progress}%</p>
          </div>
          <ProgressBar value={progress} />
          <p className="text-xs text-slate-500 mt-2">Background tasks running SAST + Secrets + Dependency checks.</p>
        </GlassCard>
        <GlassCard className="p-4 space-y-2">
          <p className="text-sm text-slate-400">Recent Findings</p>
          {findings.map((f, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 border-b border-border last:border-0">
              <div>
                <p className="text-sm text-white">{f.name}</p>
                <p className="text-xs text-slate-500">{f.file} · line {f.line}</p>
              </div>
              <SeverityBadge level={f.severity} />
            </div>
          ))}
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-sm text-slate-400 mb-2">Scan tips</p>
          <ul className="text-xs text-slate-500 space-y-1">
            <li>• Avoid uploading production secrets; use redacted samples.</li>
            <li>• Include dependency manifests for full coverage.</li>
            <li>• Turn on API key scanning in Settings.</li>
          </ul>
        </GlassCard>
      </div>
    </div>
  );
};

export default Scan;
