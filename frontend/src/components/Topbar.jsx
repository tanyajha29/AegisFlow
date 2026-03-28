import React, { useMemo } from 'react';
import { BellIcon, Bars3Icon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import { ShieldCheckIcon } from '@heroicons/react/24/solid';

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
    <header className="sticky top-0 z-20 border-b border-white/[0.06] bg-slate-950/80 backdrop-blur-2xl shadow-[0_10px_40px_rgba(0,0,0,0.35)]">
      <div className="flex items-center gap-4 px-5 py-3 md:px-6">
        {/* Mobile hamburger */}
        <button
          className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition"
          onClick={onToggleSidebar}
        >
          <Bars3Icon className="h-5 w-5" />
        </button>

        {/* Page title */}
        <div className="flex items-center gap-3">
          <span className="hidden sm:block h-8 w-px bg-white/10" />
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.15 }}
            className="flex flex-col"
          >
            <span className="text-[11px] uppercase tracking-[0.28em] text-slate-500">Command Center</span>
            <span className="text-sm font-semibold text-white">{title}</span>
          </motion.div>
        </div>

        <div className="flex-1" />

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative h-9 w-9 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-slate-400 hover:text-white hover:border-white/20 transition"
          >
            <BellIcon className="h-4.5 w-4.5 h-[18px] w-[18px]" />
            <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 bg-accent rounded-full" />
          </motion.button>

          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-cyber to-accent flex items-center justify-center shadow-[0_0_12px_rgba(34,211,238,0.25)] border border-white/10">
            <ShieldCheckIcon className="h-5 w-5 text-white" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
