import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const ChartCard = ({ title, children, action, className = '' }) => (
  <motion.div
    whileHover={{ y: -4, scale: 1.005 }}
    className={clsx(
      'relative overflow-hidden rounded-2xl border border-white/10 bg-surface/80 backdrop-blur-xl p-5 shadow-[0_20px_60px_rgba(0,0,0,0.45)]',
      'flex flex-col',
      className
    )}
  >
    <div className="pointer-events-none absolute inset-px rounded-[14px] bg-gradient-to-br from-white/5 via-transparent to-accent/10 opacity-70" />
    <div className="relative z-10 flex-1 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-semibold text-white">{title}</p>
        {action}
      </div>
      <div className="flex-1 min-h-[14rem]">{children}</div>
    </div>
  </motion.div>
);

export default ChartCard;
