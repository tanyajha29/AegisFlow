import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard.jsx';
import ScanTabs from '../components/ScanTabs.jsx';
import ScanProgress from '../components/ScanProgress.jsx';
import { useScan } from '../context/ScanContext.jsx';

const Scan = () => {
  const [code, setCode] = useState('// Paste your code here\n');
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState('code');
  const [isScanning, setIsScanning] = useState(false);
  const [localError, setLocalError] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [repoUrl, setRepoUrl] = useState('');
  const { runCodeScan, runUploadScan, runRepoScan, loading } = useScan();
  const navigate = useNavigate();

  useEffect(() => {
    let timer;
    if (isScanning) {
      timer = setInterval(() => setProgress((prev) => Math.min(prev + 8, 92)), 450);
    }
    return () => clearInterval(timer);
  }, [isScanning]);

  const handleStartScan = async () => {
    setLocalError('');
    setIsScanning(true);
    setProgress(12);
    try {
      if (activeTab === 'code') {
        await runCodeScan({ code, file_name: 'snippet.py' });
      } else if (activeTab === 'file') {
        if (!selectedFiles.length) throw new Error('Choose at least one file to upload.');
        await runUploadScan(selectedFiles);
      } else if (activeTab === 'github') {
        if (!repoUrl) throw new Error('Enter a repository URL.');
        await runRepoScan(repoUrl);
      }
      setProgress(100);
      setTimeout(() => {
        setIsScanning(false);
        navigate('/results');
      }, 250);
    } catch (err) {
      setLocalError(err?.response?.data?.detail || err.message || 'Scan failed.');
      setIsScanning(false);
      setProgress(0);
    }
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event?.target?.files || []);
    if (files.length) {
      setSelectedFiles(files);
      setLocalError('');
    }
  };

  return (
    <motion.div className="space-y-6" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Scan Workspace</p>
          <h1 className="text-3xl font-semibold text-white">Run a deep security scan</h1>
          <p className="text-slate-500 text-sm">Paste code, upload a file, or scan a GitHub repo.</p>
        </div>
      </div>

      {localError && <GlassCard className="p-3 text-sm text-red-400 border-red-500/40 bg-red-500/10">{localError}</GlassCard>}

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <ScanTabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            isScanning={isScanning || loading}
            onStartScan={handleStartScan}
            onFileSelect={handleFileSelect}
            onRepoChange={setRepoUrl}
            repoUrl={repoUrl}
            code={code}
            setCode={setCode}
            selectedFiles={selectedFiles}
          />
        </div>
        <div className="space-y-4">
          <ScanProgress
            progress={progress}
            isScanning={isScanning || loading}
            onCancel={() => {
              setIsScanning(false);
              setProgress(0);
            }}
          />
          <GlassCard className="p-4">
            <p className="text-sm text-slate-400 mb-2">Scan tips</p>
            <ul className="text-xs text-slate-500 space-y-1">
              <li>• Avoid uploading production secrets; use redacted samples.</li>
              <li>• Include dependency manifests for full coverage.</li>
              <li>• GitHub scans use the default branch.</li>
            </ul>
          </GlassCard>
        </div>
      </div>
    </motion.div>
  );
};

export default Scan;
