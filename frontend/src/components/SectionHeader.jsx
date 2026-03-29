import React from 'react';
import { motion } from 'framer-motion';

/**
 * Reusable page header used across dashboard screens.
 * Keeps typography, spacing, and actions consistent with the landing page hero.
 */
const SectionHeader = ({ eyebrow, title, description, actions = null, align = 'start' }) => {
  return (
    <div className={`flex flex-col gap-3 ${align === 'center' ? 'items-center text-center' : 'items-start'} w-full`}>
      <div className={`w-full flex flex-col gap-3 md:flex-row md:items-center ${align === 'center' ? 'md:justify-center' : 'md:justify-between'}`}>
        <div className={`${align === 'center' ? 'text-center' : 'text-left'} space-y-2 min-w-0`}>
          {eyebrow && (
            <motion.span
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-[11px] tracking-[0.3em] uppercase text-slate-400"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
              {eyebrow}
            </motion.span>
          )}

          <motion.h1
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="text-2xl md:text-3xl font-bold text-white leading-tight"
          >
            {title}
          </motion.h1>

          {description && (
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-sm text-slate-400 max-w-3xl"
            >
              {description}
            </motion.p>
          )}
        </div>

        {actions && <div className="flex flex-wrap gap-3 justify-end md:ml-6">{actions}</div>}
      </div>
    </div>
  );
};

export default SectionHeader;
