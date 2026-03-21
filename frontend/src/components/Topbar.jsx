import React, { useMemo } from 'react';
import { BellIcon, Bars3Icon, EyeIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';

const routeTitle = (pathname) => {
  if (pathname.startsWith('/app/scan')) return 'Scan Workspace';
  if (pathname.startsWith('/app/results')) return 'Scan Results';
  if (pathname.startsWith('/app/reports')) return 'Security Reports';
  if (pathname.startsWith('/app/history')) return 'Scan History';
  if (pathname.startsWith('/app/settings')) return 'Settings';
  if (pathname.startsWith('/app')) return 'Dashboard';
  return 'DristiScan';
};

const Topbar = ({ onToggleSidebar }) => {
  const { pathname } = useLocation();
  const title = useMemo(() => routeTitle(pathname), [pathname]);

  return (
    <header className="sticky top-0 z-20">
      <div className="max-w-7xl mx-auto flex items-center gap-3 px-6 py-4 md:px-10 glass-card bg-[rgba(15,23,42,0.85)] border border-[rgba(59,130,246,0.25)] backdrop-blur-2xl">
        <button className="md:hidden text-slate-300" onClick={onToggleSidebar}>
          <Bars3Icon className="h-6 w-6" />
        </button>
        <motion.div
          key={title}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.18 }}
          className="flex items-center gap-2 text-slate-100"
        >
          <span className="text-sm uppercase tracking-[0.18em] text-slate-500">Page</span>
          <span className="h-5 w-px bg-slate-700" />
          <span className="text-lg font-semibold">{title}</span>
        </motion.div>
        <div className="flex-1" />
        <motion.button
          whileHover={{ scale: 1.05 }}
          className="relative h-11 w-11 rounded-xl bg-surface border border-border flex items-center justify-center"
        >
          <BellIcon className="h-5 w-5 text-slate-200" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-accent rounded-full animate-pulse" />
        </motion.button>
        <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-cyber to-accent flex items-center justify-center text-white">
          <EyeIcon className="h-6 w-6" />
        </div>
      </div>
    </header>
  );
};

export default Topbar;
