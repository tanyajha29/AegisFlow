import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import GlassCard from "../components/GlassCard.jsx";
import ScanTabs from "../components/ScanTabs.jsx";
import ScanProgress from "../components/ScanProgress.jsx";
import { useScan } from "../context/ScanContext.jsx";

const Scan = () => {
  const [code, setCode] = useState("// Paste your code here\n");
  const [progress, setProgress] = useState(0);
  const [activeTab, setActiveTab] = useState("code");
  const [isScanning, setIsScanning] = useState(false);
  const [localError, setLocalError] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [repoUrl, setRepoUrl] = useState("");
  const { runCodeScan, runUploadScan, runRepoScan, loading } = useScan();
  const navigate = useNavigate();

  useEffect(() => {
    let timer;
    if (isScanning) {
      timer = setInterval(() => setProgress((prev) => Math.min(prev + 8, 92)), 450);
    }
    return () => clearInterval(timer);
  }, [isScanning]);

  const handleCancel = () => {
    setIsScanning(false);
    setProgress(0);
  };

  const handleStartScan = async () => {
    setLocalError("");
    setIsScanning(true);
    setProgress(12);
    try {
      if (activeTab === "code") {
        await runCodeScan({ code, file_name: "snippet.py" });
      } else if (activeTab === "file") {
        if (!selectedFiles.length) throw new Error("Choose at least one file to upload.");
        await runUploadScan(selectedFiles);
      } else if (activeTab === "github") {
        if (!repoUrl) throw new Error("Enter a repository URL.");
        await runRepoScan(repoUrl);
      }
      setProgress(100);
      setTimeout(() => {
        setIsScanning(false);
        navigate("/app/results");
      }, 250);
    } catch (err) {
      setLocalError(err?.response?.data?.detail || err.message || "Scan failed.");
      setIsScanning(false);
      setProgress(0);
    }
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event?.target?.files || []);
    if (files.length) {
      setSelectedFiles(files);
      setLocalError("");
    }
  };

  return (
    <motion.div className="space-y-6" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      {/* Page header */}
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-500">Scan Workspace</p>
        <h1 className="text-2xl font-bold text-white mt-1">Run a deep security scan</h1>
        <p className="text-sm text-slate-500 mt-1">Paste code, upload a file, or scan a GitHub repo.</p>
      </div>

      {localError && (
        <GlassCard className="p-3 text-sm text-red-400 border-red-500/40 bg-red-500/10">
          {localError}
        </GlassCard>
      )}

      <div className="grid lg:grid-cols-3 gap-5">
        {/* Main scan input — takes 2/3 */}
        <div className="lg:col-span-2">
          <ScanTabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            isScanning={isScanning || loading}
            onStartScan={handleStartScan}
            onCancel={handleCancel}
            onFileSelect={handleFileSelect}
            onRepoChange={setRepoUrl}
            repoUrl={repoUrl}
            code={code}
            setCode={setCode}
            selectedFiles={selectedFiles}
          />
        </div>

        {/* Progress panel — takes 1/3 */}
        <div>
          <ScanProgress
            progress={progress}
            isScanning={isScanning || loading}
            onCancel={handleCancel}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default Scan;
