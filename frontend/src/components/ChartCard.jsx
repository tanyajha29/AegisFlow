import React from 'react';
import { motion } from 'framer-motion';

const ChartCard = ({ title, children, action }) => (
  <motion.div whileHover={{ y: -2 }} className="glass rounded-2xl p-4 md:p-5">
    <div className="flex items-center justify-between mb-3">
      <p className="text-sm text-slate-400">{title}</p>
      {action}
    </div>
    <div className="h-64">{children}</div>
  </motion.div>
);

export default ChartCard;
