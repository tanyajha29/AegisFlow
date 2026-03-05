import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ title, value, subtext, icon: Icon, color }) => (
  <motion.div
    whileHover={{ y: -2 }}
    className="glass rounded-2xl p-4 border border-border shadow-glass"
  >
    <div className="flex items-center justify-between">
      <div className="space-y-1">
        <p className="text-sm text-slate-400">{title}</p>
        <p className="text-2xl font-semibold text-white">{value}</p>
        {subtext && <p className="text-xs text-slate-500">{subtext}</p>}
      </div>
      {Icon && (
        <div className={`h-11 w-11 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="h-5 w-5 text-white" />
        </div>
      )}
    </div>
  </motion.div>
);

export default StatCard;
