import { useMemo } from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';
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
    <header
      className="flex-shrink-0 z-20 border-b border-[rgba(59,130,246,0.12)] backdrop-blur-2xl"
      style={{ background: 'rgba(11,18,32,0.85)' }}
    >
      <div className="flex items-center gap-4 px-8 py-5 md:px-6">
        <button
          className="md:hidden p-1.5 rounded-lg text-[#94A3B8] hover:text-white hover:bg-white/5 transition"
          onClick={onToggleSidebar}
        >
          <Bars3Icon className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-3">
          <span className="text-[11px] uppercase tracking-[0.22em] text-[#475569] font-medium">Page</span>
          <span className="h-5 w-px bg-[rgba(59,130,246,0.25)]" />
          <span className="text-sm font-semibold text-[#E2E8F0]">{title}</span>
        </div>

        <div className="flex-1" />

        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#06B6D4] flex items-center justify-center shadow-[0_0_14px_rgba(59,130,246,0.35)] border border-white/10">
          <ShieldCheckIcon className="h-5 w-5 text-white" />
        </div>
      </div>
    </header>
  );
};

export default Topbar;
