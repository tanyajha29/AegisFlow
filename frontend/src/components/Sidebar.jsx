import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  EyeIcon,
  HomeModernIcon,
  CodeBracketSquareIcon,
  ArrowUpOnSquareStackIcon,
  ClockIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  ArrowRightStartOnRectangleIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext.jsx';

const mainNav = [
  { to: '/app', label: 'Dashboard', icon: HomeModernIcon },
  { to: '/app/scan', label: 'Scan Code', icon: CodeBracketSquareIcon },
  { to: '/app/results', label: 'Scan Results', icon: ArrowUpOnSquareStackIcon },
  { to: '/app/history', label: 'Scan History', icon: ClockIcon },
];

const secondaryNav = [
  { to: '/app/reports', label: 'Security Reports', icon: DocumentTextIcon },
  { to: '/app/settings', label: 'Settings', icon: Cog6ToothIcon },
];

const NavItem = ({ to, label, icon: Icon, collapsed }) => (
  <NavLink
    to={to}
    end={to === '/app'}
    className={({ isActive }) =>
      `group relative flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
        isActive
          ? 'bg-blue-500/15 border border-blue-500/30 text-white shadow-[0_0_12px_rgba(59,130,246,0.2)]'
          : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent hover:border-blue-500/20'
      }`
    }
    title={collapsed ? label : undefined}
  >
    <Icon className="h-5 w-5 flex-shrink-0" />
    {!collapsed && <span className="text-sm font-medium truncate">{label}</span>}
  </NavLink>
);

const Sidebar = ({ collapsed, onToggle }) => {
  const { logout } = useAuth();

  return (
    <aside
      className={`fixed md:sticky top-0 left-0 z-30 h-screen flex flex-col bg-gradient-to-b from-slate-950/98 to-slate-950/95 border-r border-blue-500/10 backdrop-blur-xl transition-all duration-300 ${
        collapsed ? '-translate-x-full md:translate-x-0 md:w-[70px]' : 'translate-x-0 w-64'
      }`}
    >
      {/* Brand */}
      <div className={`flex items-center gap-3 px-4 py-6 border-b border-blue-500/10 ${collapsed ? 'justify-center' : ''}`}>
        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.4),0_0_40px_rgba(6,182,212,0.2)] flex-shrink-0">
          <EyeIcon className="h-5 w-5 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-white font-bold text-sm leading-tight">DristiScan</p>
            <p className="text-[11px] text-slate-500 truncate">See the risks early</p>
          </div>
        )}
      </div>

      {/* Main nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-5 space-y-1.5 scrollbar-thin scrollbar-thumb-blue-500/20 scrollbar-track-transparent">
        {!collapsed && (
          <p className="text-[10px] uppercase tracking-widest text-slate-600 px-2 mb-3">Workspace</p>
        )}
        {mainNav.map((item) => (
          <NavItem key={item.to} {...item} collapsed={collapsed} />
        ))}

        <div className={`my-4 border-t border-blue-500/10 ${collapsed ? 'mx-1' : 'mx-0'}`} />

        {!collapsed && (
          <p className="text-[10px] uppercase tracking-widest text-slate-600 px-2 mb-3">Reports</p>
        )}
        {secondaryNav.map((item) => (
          <NavItem key={item.to} {...item} collapsed={collapsed} />
        ))}
      </nav>

      {/* Bottom area */}
      <div className="px-3 py-4 border-t border-blue-500/10 space-y-2 mt-auto">
        <button
          onClick={logout}
          title={collapsed ? 'Logout' : undefined}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-red-300 hover:bg-red-500/10 border border-transparent hover:border-red-500/20 transition-all text-sm font-medium ${collapsed ? 'justify-center' : ''}`}
        >
          <ArrowRightStartOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>

        {/* Collapse toggle — desktop only */}
        <button
          onClick={onToggle}
          className={`hidden md:flex w-full items-center gap-3 px-3 py-2 rounded-lg text-slate-600 hover:text-slate-300 hover:bg-blue-500/10 transition-all text-xs ${collapsed ? 'justify-center' : ''}`}
        >
          {collapsed ? (
            <ChevronRightIcon className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeftIcon className="h-4 w-4" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>

      {/* Mobile close button */}
      <button
        className="md:hidden absolute top-4 right-4 text-slate-400 hover:text-white transition"
        onClick={onToggle}
      >
        ✕
      </button>
    </aside>
  );
};

export default Sidebar;
