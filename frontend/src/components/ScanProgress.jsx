import React from 'react';
import { motion } from 'framer-motion';
import { Shield, CheckCircle, X } from 'lucide-react';

const scanSteps = [
  { label: 'Initializing', completion: 5 },
  { label: 'Analyzing Dependencies', completion: 25 },
  { label: 'Code Inspection', completion: 50 },
  { label: 'Vulnerability Detection', completion: 75 },
  { label: 'Report Generation', completion: 90 },
  { label: 'Finalizing', completion: 100 },
];

const ScanProgress = ({ progress, isScanning, onCancel }) => {
  const currentStep =
    scanSteps.find((step, idx) => progress >= (scanSteps[idx - 1]?.completion || 0) && progress < step.completion) ||
    scanSteps[scanSteps.length - 1];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative rounded-2xl border border-white/10 bg-surface/80 backdrop-blur-xl p-6 overflow-hidden h-full flex flex-col shadow-[0_20px_60px_rgba(0,0,0,0.45)]"
    >
      <motion.div
        className="absolute inset-0 opacity-20"
        animate={{
          background: [
            'linear-gradient(45deg, transparent, rgba(34,211,238,0.4), transparent)',
            'linear-gradient(225deg, transparent, rgba(37,99,235,0.35), transparent)',
          ],
        }}
        transition={{ repeat: Infinity, duration: 4 }}
      />

      <div className="relative z-10 flex flex-col h-full">
        <div className="mb-6 flex items-center gap-3">
          <motion.div
            animate={{ rotate: isScanning ? 360 : 0 }}
            transition={{ repeat: isScanning ? Infinity : 0, duration: 2, ease: 'linear' }}
          >
            <Shield size={22} className="text-accent" />
          </motion.div>
          <div>
            <h3 className="text-lg font-semibold text-white">{isScanning ? 'Scanning...' : 'Ready to Scan'}</h3>
            {isScanning && <p className="text-xs text-slate-400">{currentStep?.label}</p>}
          </div>
        </div>

        {isScanning && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs uppercase tracking-wide text-slate-400">Progress</p>
              <motion.span className="text-sm font-semibold text-accent" key={Math.floor(progress / 5)}>
                {Math.round(progress)}%
              </motion.span>
            </div>
            <div className="w-full h-2 bg-white/5 border border-white/10 rounded-full overflow-hidden relative">
              <motion.div
                className="h-full bg-gradient-to-r from-accent to-cyber rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.25 }}
              />
              <motion.div
                className="absolute inset-0 mix-blend-screen"
                style={{
                  background:
                    'linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.45) 50%, transparent 100%)',
                }}
                animate={{ x: ['-120%', '120%'] }}
                transition={{ repeat: Infinity, duration: 1.4, ease: 'linear' }}
              />
            </div>
          </div>
        )}

        <div className="space-y-2 flex-1 mb-6">
          {scanSteps.map((step, idx) => {
            const isCompleted = progress >= step.completion;
            const isActive = currentStep === step && isScanning;
            return (
              <motion.div
                key={step.label}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.04 }}
                className={`flex items-center gap-3 p-2 rounded ${
                  isCompleted || isActive ? 'text-accent' : 'text-slate-500'
                }`}
              >
                <motion.div animate={isActive ? { scale: [1, 1.08, 1] } : {}}>
                  {isCompleted ? <CheckCircle size={16} /> : <div className="w-4 h-4 rounded-full border border-current" />}
                </motion.div>
                <span className="text-xs">{step.label}</span>
              </motion.div>
            );
          })}
        </div>

        {isScanning && (
          <motion.button
            onClick={onCancel}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            className="w-full py-2 px-3 flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/15 text-red-400 rounded-lg text-sm font-medium"
          >
            <X size={16} />
            Cancel Scan
          </motion.button>
        )}
      </div>
    </motion.div>
  );
};

export default ScanProgress;

