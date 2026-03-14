import React from 'react';
import { motion } from 'framer-motion';
import { Download, FileText, Calendar, AlertCircle } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.25 } },
};

const severityColors = {
  Critical: { text: 'text-critical', bg: 'bg-critical/10' },
  High: { text: 'text-high', bg: 'bg-high/10' },
  Medium: { text: 'text-medium', bg: 'bg-medium/10' },
  Low: { text: 'text-low', bg: 'bg-low/10' },
};

const ReportsList = ({ reports = [], onDownload }) => {
  return (
    <motion.div
      className="relative rounded-lg border border-border bg-card p-6 overflow-hidden shadow-glow"
      whileHover={{ scale: 1.01 }}
    >
      <motion.div
        className="absolute inset-0 opacity-5"
        animate={{
          background: [
            'linear-gradient(45deg, transparent, rgba(34,211,238,0.35), transparent)',
            'linear-gradient(225deg, transparent, rgba(37,99,235,0.3), transparent)',
          ],
        }}
        transition={{ repeat: Infinity, duration: 4 }}
      />

      <div className="relative z-10">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-white">Available Reports</h3>
          <p className="text-sm text-slate-400">
            {reports.length} report{reports.length !== 1 ? 's' : ''} available
          </p>
        </div>

        <motion.div className="hidden lg:grid grid-cols-12 gap-4 px-4 py-3 border-b border-border mb-2">
          <div className="col-span-4 text-xs font-semibold text-slate-400 uppercase">Report</div>
          <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase">Date</div>
          <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase">Issues</div>
          <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase">Format</div>
          <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase text-right">Action</div>
        </motion.div>

        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-3">
          {reports.map((r) => {
            const colors = severityColors[r.risk_level?.includes('High') ? 'High' : r.risk_level?.includes('Critical') ? 'Critical' : r.risk_level?.includes('Medium') ? 'Medium' : 'Low'] ||
              severityColors.Low;
            return (
              <motion.div
                key={r.scan_id}
                variants={itemVariants}
                whileHover={{ scale: 1.01, x: 3 }}
                className="hidden lg:grid grid-cols-12 gap-4 p-4 rounded-lg border border-border/60 hover:border-border hover:bg-card/50 transition-all"
              >
                <div className="col-span-4 flex items-center gap-3">
                  <motion.div animate={{ y: [0, -2, 0] }} transition={{ repeat: Infinity, duration: 2 }}>
                    <FileText size={20} className="text-accent" />
                  </motion.div>
                  <div className="flex-1">
                    <p className="font-medium text-white text-sm">{r.file_name}</p>
                    <p className="text-xs text-slate-500">Scan #{r.scan_id}</p>
                  </div>
                </div>
                <div className="col-span-2 flex items-center gap-2 text-sm text-white">
                  <Calendar size={16} className="text-slate-400" />
                  {new Date(r.scan_date).toLocaleDateString()}
                </div>
                <div className="col-span-2 flex items-center gap-2">
                  <AlertCircle size={16} className={colors.text} />
                  <div>
                    <p className="text-sm font-semibold text-white">{r.total_vulnerabilities}</p>
                    <p className={`text-xs font-bold ${colors.text}`}>{r.risk_level}</p>
                  </div>
                </div>
                <div className="col-span-2 flex items-center">
                  <span className="px-3 py-1 rounded-full bg-accent/10 text-accent text-xs font-semibold uppercase">PDF</span>
                </div>
                <div className="col-span-2 flex items-center justify-end">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.92 }}
                    className="p-2 rounded-lg hover:bg-accent/20 text-accent transition-colors"
                    onClick={() => onDownload?.(r.scan_id, r.file_name)}
                  >
                    <Download size={18} />
                  </motion.button>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="lg:hidden space-y-3">
          {reports.map((r) => {
            const colors = severityColors[r.risk_level?.includes('High') ? 'High' : r.risk_level?.includes('Critical') ? 'Critical' : r.risk_level?.includes('Medium') ? 'Medium' : 'Low'] ||
              severityColors.Low;
            return (
              <motion.div
                key={r.scan_id}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                className="p-4 rounded-lg border border-border/60 hover:border-border hover:bg-card/50 transition-all"
              >
                <div className="flex items-start gap-3 mb-3">
                  <FileText size={20} className="text-accent flex-shrink-0" />
                  <div className="flex-1">
                    <p className="font-medium text-white text-sm">{r.file_name}</p>
                    <p className="text-xs text-slate-500">Scan #{r.scan_id} • {new Date(r.scan_date).toLocaleDateString()}</p>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.92 }}
                    className="p-2 rounded-lg hover:bg-accent/20 text-accent transition-colors"
                    onClick={() => onDownload?.(r.scan_id, r.file_name)}
                  >
                    <Download size={18} />
                  </motion.button>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className={`px-2 py-1 rounded-full ${colors.bg} ${colors.text} font-semibold`}>{r.risk_level}</span>
                  <span className="text-slate-400">{r.total_vulnerabilities} issues</span>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ReportsList;
