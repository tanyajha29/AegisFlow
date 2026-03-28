import React from 'react';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';

const severities = [
  { value: null, label: 'All', color: '' },
  { value: 'Critical', label: 'Critical', color: 'bg-critical' },
  { value: 'High', label: 'High', color: 'bg-high' },
  { value: 'Medium', label: 'Medium', color: 'bg-medium' },
  { value: 'Low', label: 'Low', color: 'bg-low' },
];

const ResultsFilter = ({ selectedSeverity, onSeverityChange, searchTerm, onSearchChange }) => {
  return (
    <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
        <input
          type="text"
          placeholder="Search vulnerabilities..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]"
        />
      </div>

      <div className="flex gap-2 flex-wrap">
        {severities.map((severity) => {
          const active = selectedSeverity === severity.value;
          return (
            <motion.button
              key={severity.label}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSeverityChange(severity.value)}
              className={`px-4 py-2 rounded-xl font-medium transition-all ${
                active
                  ? 'bg-gradient-to-r from-cyber/30 via-accent/30 to-transparent text-white border border-accent/50 shadow-[0_10px_30px_rgba(34,211,238,0.25)]'
                  : 'bg-white/5 border border-white/10 text-slate-400 hover:text-white'
              }`}
            >
              {severity.label}
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ResultsFilter;
