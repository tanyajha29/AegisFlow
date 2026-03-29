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
    <header className="sticky top-0 z-20 border-b border-blue-500/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="flex items-center gap-4 px-6 py-4 md:px-8">
        {/* Mobile hamburger */}
        <button
          className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-blue-500/10 transition-all"
          onClick={onToggleSidebar}
        >
          <Bars3Icon className="h-5 w-5" />
        </button>

        {/* Page title */}
        <motion.div
          key={title}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="flex items-center gap-3"
        >
          <span className="text-[10px] uppercase tracking-widest text-blue-400/60 hidden sm:block font-semibold">Page</span>
          <span className="hidden sm:block h-5 w-px bg-blue-500/20" />
          <span className="text-base font-bold text-white">{title}</span>
        </motion.div>

        <div className="flex-1" />

        {/* Right actions */}
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative h-10 w-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-slate-400 hover:text-white hover:bg-blue-500/20 hover:border-blue-500/40 transition-all"
          >
            <BellIcon className="h-5 w-5" />
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="absolute top-1 right-1 h-2 w-2 bg-cyan-400 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.6)]"
            />
          </motion.button>

          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.4),0_0_40px_rgba(6,182,212,0.2)]">
            <ShieldCheckIcon className="h-5 w-5 text-white" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
