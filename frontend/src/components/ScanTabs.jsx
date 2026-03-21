import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Code, Upload, Github, Zap } from 'lucide-react';

const tabs = [
  { id: 'code', label: 'Code Editor', icon: Code },
  { id: 'file', label: 'File Upload', icon: Upload },
  { id: 'github', label: 'GitHub Repository', icon: Github },
];

const ScanTabs = ({
  activeTab,
  onTabChange,
  isScanning,
  onStartScan,
  onFileSelect,
  onRepoChange,
  repoUrl,
  code,
  setCode,
  selectedFiles = [],
}) => {
  return (
    <motion.div whileHover={!isScanning ? { scale: 1.005 } : {}} className="relative rounded-xl border border-border bg-card overflow-hidden shadow-glow">
      <div className="flex border-b border-border bg-surface/30">
        {tabs.map((tab, idx) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <motion.button
              key={tab.id}
              onClick={() => !isScanning && onTabChange(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-all ${
                isActive ? 'text-accent border-b-2 border-accent bg-accent/5' : 'text-slate-400 hover:text-white'
              }`}
              disabled={isScanning}
              whileHover={!isScanning ? { backgroundColor: 'rgba(34,211,238,0.04)' } : {}}
            >
              <Icon size={18} />
              {tab.label}
            </motion.button>
          );
        })}
      </div>

      <div className="p-6 min-h-[320px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.18 }}
            className="space-y-4"
          >
            {activeTab === 'code' && (
              <>
                <label className="block text-sm font-semibold text-white">Paste your code</label>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  disabled={isScanning}
                  className="w-full h-64 p-4 bg-surface border border-border rounded-lg font-mono text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-60 resize-none"
                  placeholder="// Paste your code here..."
                />
              </>
            )}

            {activeTab === 'file' && (
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent/60 transition-colors">
                <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 2 }} className="mb-4">
                  <Upload size={32} className="mx-auto text-accent" />
                </motion.div>
                <h3 className="font-semibold text-white mb-2">Upload Files</h3>
                <p className="text-sm text-slate-400 mb-4">Drag and drop files or click to browse.</p>
                <input
                  type="file"
                  multiple
                  disabled={isScanning}
                  className="hidden"
                  id="file-upload"
                  onChange={onFileSelect}
                  accept=".py,.js,.ts,.jsx,.tsx,.java,.go,.rb,.php,.cs,.c,.cpp,.json,.env,.txt"
                />
                <label
                  htmlFor="file-upload"
                  className="inline-block px-4 py-2 bg-accent/20 hover:bg-accent/30 text-accent rounded-lg cursor-pointer transition-colors"
                >
                  Browse Files
                </label>

                {selectedFiles.length > 0 && (
                  <div className="mt-4 text-left bg-surface/60 border border-border/60 rounded-lg p-3 space-y-2 max-h-40 overflow-y-auto">
                    <p className="text-xs text-slate-400">Selected files</p>
                    <ul className="text-sm text-slate-200 space-y-1">
                      {selectedFiles.map((file) => (
                        <li key={file.name} className="flex justify-between">
                          <span className="truncate">{file.name}</span>
                          <span className="text-slate-500 text-xs">{(file.size / 1024).toFixed(1)} KB</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'github' && (
              <>
                <label className="block text-sm font-semibold text-white">Repository URL</label>
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => onRepoChange(e.target.value)}
                  disabled={isScanning}
                  placeholder="https://github.com/username/repository"
                  className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-accent/50 disabled:opacity-60"
                />
                <p className="text-xs text-slate-400">Scans the default branch of the repository.</p>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="p-6 border-t border-border flex gap-4 bg-surface/40">
        <motion.button
          onClick={onStartScan}
          disabled={isScanning}
          whileHover={!isScanning ? { scale: 1.02 } : {}}
          whileTap={!isScanning ? { scale: 0.97 } : {}}
          className="flex-1 py-3 px-4 bg-gradient-to-r from-accent to-cyber rounded-lg text-navy font-semibold hover:shadow-glow text-sm disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <Zap size={18} />
          {isScanning ? 'Scanning…' : 'Start Scan'}
        </motion.button>
      </div>
    </motion.div>
  );
};

export default ScanTabs;
