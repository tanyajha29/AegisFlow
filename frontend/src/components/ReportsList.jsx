import React from 'react';
import { motion } from 'framer-motion';
import { Download, FileText, Calendar, AlertCircle, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.25 } },
};

const riskColor = (level = '') => {
  if (level.includes('Critical')) return { text: 'text-critical', bg: 'bg-critical/10' };
  if (level.includes('High'))     return { text: 'text-high',     bg: 'bg-high/10' };
  if (level.includes('Medium'))   return { text: 'text-medium',   bg: 'bg-medium/10' };
  return                                 { text: 'text-low',      bg: 'bg-low/10' };
};

const ActionButtons = ({ scanId, fileName, onDownload }) => {
  const navigate = useNavigate();
  return (
    <div className="flex items-center gap-1 justify-end">
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.92 }}
        title="View Report"
        className="p-2 rounded-lg hover:bg-white/10 text-slate-300 hover:text-white transition-colors"
        onClick={() => navigate(`/app/reports/${scanId}`)}
      >
        <Eye size={17} />
      </motion.button>
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.92 }}
        title="Download PDF"
        className="p-2 rounded-lg hover:bg-accent/20 text-accent transition-colors"
        onClick={() => onDownload?.(scanId, fileName)}
      >
        <Download size={17} />
      </motion.button>
    </div>
  );
};

const ReportsList = ({ reports = [], onDownload }) => {
  return (
    <motion.div
      className="relative rounded-lg border border-border bg-card p-6 overflow-hidden shadow-glow"
    >
      <motion.div
        className="absolute inset-0 opacity-5 pointer-events-none"
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

        {/* Desktop table */}
        <div className="hidden lg:block">
          <div className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-border mb-2">
            <div className="col-span-4 text-xs font-semibold text-slate-400 uppercase">Report</div>
            <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase">Date</div>
            <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase">Issues</div>
            <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase">Format</div>
            <div className="col-span-2 text-xs font-semibold text-slate-400 uppercase text-right">Actions</div>
          </div>

          <motion.div variants={containerVariants} initial="hidden" animate="visible" className="space-y-2">
            {reports.length === 0 && (
              <p className="text-slate-500 text-sm px-4 py-6 text-center">No reports yet.</p>
            )}
            {reports.map((r) => {
              const colors = riskColor(r.risk_level);
              const fileName = r.display_file_name || r.file_name;
              return (
                <motion.div
                  key={r.scan_id}
                  variants={itemVariants}
                  whileHover={{ x: 2 }}
                  className="grid grid-cols-12 gap-4 p-4 rounded-lg border border-border/60 hover:border-border hover:bg-white/[0.03] transition-all"
                >
                  <div className="col-span-4 flex items-center gap-3">
                    <FileText size={18} className="text-accent flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="font-medium text-white text-sm truncate">{fileName}</p>
                      <p className="text-xs text-slate-500">Scan #{r.scan_id}</p>
                    </div>
                  </div>
                  <div className="col-span-2 flex items-center gap-2 text-sm text-slate-300">
                    <Calendar size={14} className="text-slate-500 flex-shrink-0" />
                    {new Date(r.scan_date).toLocaleDateString()}
                  </div>
                  <div className="col-span-2 flex items-center gap-2">
                    <AlertCircle size={14} className={colors.text} />
                    <div>
                      <p className="text-sm font-semibold text-white">{r.total_vulnerabilities}</p>
                      <p className={`text-xs font-semibold ${colors.text}`}>{r.risk_level}</p>
                    </div>
                  </div>
                  <div className="col-span-2 flex items-center">
                    <span className="px-2.5 py-1 rounded-full bg-accent/10 text-accent text-xs font-semibold uppercase">
                      PDF
                    </span>
                  </div>
                  <div className="col-span-2 flex items-center justify-end">
                    <ActionButtons scanId={r.scan_id} fileName={fileName} onDownload={onDownload} />
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>

        {/* Mobile cards */}
        <motion.div variants={containerVariants} initial="hidden" animate="visible" className="lg:hidden space-y-3">
          {reports.map((r) => {
            const colors = riskColor(r.risk_level);
            const fileName = r.display_file_name || r.file_name;
            return (
              <motion.div
                key={r.scan_id}
                variants={itemVariants}
                className="p-4 rounded-lg border border-border/60 hover:border-border hover:bg-card/50 transition-all"
              >
                <div className="flex items-start gap-3 mb-3">
                  <FileText size={18} className="text-accent flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-white text-sm truncate">{fileName}</p>
                    <p className="text-xs text-slate-500">Scan #{r.scan_id} · {new Date(r.scan_date).toLocaleDateString()}</p>
                  </div>
                  <ActionButtons scanId={r.scan_id} fileName={fileName} onDownload={onDownload} />
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className={`px-2 py-1 rounded-full ${colors.bg} ${colors.text} font-semibold`}>
                    {r.risk_level}
                  </span>
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
