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
      `group relative flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition-all duration-150 ${
        isActive
          ? 'bg-gradient-to-r from-white/5 via-accent/10 to-transparent border border-accent/30 text-white shadow-[0_10px_40px_rgba(34,211,238,0.25)] before:absolute before:left-0.5 before:top-2 before:bottom-2 before:w-[3px] before:rounded-full before:bg-accent before:content-[\"\"]'
          : 'text-slate-400 hover:text-slate-100 hover:bg-white/5 border border-white/[0.02]'
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
      className={`fixed md:static z-30 h-screen flex flex-col bg-slate-950/90 border-r border-white/[0.08] backdrop-blur-2xl shadow-[0_20px_80px_rgba(0,0,0,0.55)] transition-all duration-300 ${
        collapsed ? '-translate-x-full md:translate-x-0 md:w-[68px]' : 'translate-x-0 w-64'
      }`}
    >
      {/* Brand */}
      <div className={`flex items-center gap-3 px-4 py-5 border-b border-white/[0.06] ${collapsed ? 'justify-center' : ''}`}>
        <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-cyber to-accent flex items-center justify-center shadow-[0_0_16px_rgba(34,211,238,0.35)] flex-shrink-0 ring-1 ring-white/10">
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
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {!collapsed && (
          <p className="text-[10px] uppercase tracking-[0.25em] text-slate-600 px-3 mb-2">Workspace</p>
        )}
        {mainNav.map((item) => (
          <NavItem key={item.to} {...item} collapsed={collapsed} />
        ))}

        <div className={`my-3 border-t border-white/[0.06] ${collapsed ? 'mx-1' : 'mx-0'}`} />

        {!collapsed && (
          <p className="text-[10px] uppercase tracking-widest text-slate-600 px-3 mb-2">Reports</p>
        )}
        {secondaryNav.map((item) => (
          <NavItem key={item.to} {...item} collapsed={collapsed} />
        ))}
      </nav>

      {/* Bottom area */}
      <div className="px-3 py-4 border-t border-white/[0.06] space-y-2">
        <button
          onClick={logout}
          title={collapsed ? 'Logout' : undefined}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-400 hover:text-red-400 hover:bg-red-500/5 border border-red-500/10 transition-all text-sm font-medium ${collapsed ? 'justify-center' : ''}`}
        >
          <ArrowRightStartOnRectangleIcon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>

        {/* Collapse toggle - desktop only */}
        <button
          onClick={onToggle}
          className={`hidden md:flex w-full items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:text-slate-300 hover:bg-white/5 transition-all text-xs ${collapsed ? 'justify-center' : ''}`}
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
        className="md:hidden absolute top-4 right-4 text-slate-400 hover:text-white"
        onClick={onToggle}
      >
        X
      </button>
    </aside>
  );
};

export default Sidebar;

