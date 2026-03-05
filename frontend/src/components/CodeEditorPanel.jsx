import React from 'react';
import { CodeBracketSquareIcon, DocumentArrowUpIcon, PlayIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

const CodeEditorPanel = ({ code, setCode, language, setLanguage, onUpload, onRun }) => {
  const languages = ['python', 'javascript', 'java', 'php', 'text'];

  return (
    <div className="grid md:grid-cols-3 gap-4">
      <div className="md:col-span-2 glass rounded-2xl border border-border p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CodeBracketSquareIcon className="h-5 w-5 text-accent" />
            <p className="text-sm text-slate-400">Code Editor</p>
          </div>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="bg-surface border border-border rounded-lg px-3 py-2 text-sm"
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
        <div className="bg-[#0B1224] border border-border rounded-xl relative overflow-hidden">
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste or write your code here..."
            className="w-full h-[360px] p-4 bg-transparent text-sm font-mono text-slate-100 outline-none resize-none"
          />
          <div className="absolute inset-x-0 top-0 h-8 bg-gradient-to-r from-cyber/20 via-accent/10 to-cyber/20 opacity-60" />
        </div>
      </div>
      <div className="glass rounded-2xl border border-border p-4 space-y-3">
        <p className="text-sm text-slate-400">Scan Controls</p>
        <motion.button
          whileHover={{ scale: 1.02 }}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-cyber to-accent text-white font-semibold shadow-glow"
          onClick={onRun}
        >
          <PlayIcon className="h-5 w-5" />
          Run Scan
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-border text-slate-200"
          onClick={onUpload}
        >
          <DocumentArrowUpIcon className="h-5 w-5" />
          Upload File
        </motion.button>
        <p className="text-xs text-slate-500">
          Supported: .py, .js, .java, .php, .txt. Files are stored temporarily and auto-deleted after scanning.
        </p>
      </div>
    </div>
  );
};

export default CodeEditorPanel;
