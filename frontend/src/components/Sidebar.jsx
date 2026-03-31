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

// eslint-disable-next-line no-unused-vars
const NavItem = ({ to, label, icon: Icon, collapsed }) => (
  <NavLink
    to={to}
    end={to === '/app'}
    className={({ isActive }) =>
      `group relative flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 ${
        isActive
          ? 'bg-[rgba(59,130,246,0.12)] border border-[rgba(59,130,246,0.35)] text-white shadow-[0_0_20px_rgba(59,130,246,0.15)]'
          : 'text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[rgba(59,130,246,0.06)] border border-transparent'
      }`
    }
    title={collapsed ? label : undefined}
  >
    {({ isActive }) => (
      <>
        {isActive && (
          <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r-full bg-gradient-to-b from-[#3B82F6] to-[#06B6D4]" />
        )}
        <Icon className="h-[18px] w-[18px] flex-shrink-0" />
        {!collapsed && <span className="text-sm font-medium truncate">{label}</span>}
      </>
    )}
  </NavLink>
);

const Sidebar = ({ collapsed, onToggle }) => {
  const { logout } = useAuth();

  return (
    <aside
      className={`flex-shrink-0 h-screen flex flex-col border-r border-[rgba(59,130,246,0.12)] backdrop-blur-2xl transition-all duration-300 relative z-30 ${
        collapsed ? 'w-[68px]' : 'w-60'
      }`}
      style={{
        background: 'linear-gradient(180deg, rgba(11,18,32,0.97) 0%, rgba(15,23,42,0.95) 100%)',
      }}
    >
      {/* Subtle right edge glow */}
      <div className="absolute inset-y-0 right-0 w-px bg-gradient-to-b from-transparent via-[rgba(59,130,246,0.2)] to-transparent pointer-events-none" />

      {/* Brand */}
      <div className={`flex items-center gap-3 px-4 py-5 border-b border-[rgba(59,130,246,0.1)] flex-shrink-0 ${collapsed ? 'justify-center' : ''}`}>
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[#3B82F6] to-[#06B6D4] flex items-center justify-center shadow-[0_0_16px_rgba(59,130,246,0.4)] flex-shrink-0 ring-1 ring-white/10">
          <EyeIcon className="h-5 w-5 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-[#E2E8F0] font-bold text-sm leading-tight">DristiScan</p>
            <p className="text-[10px] text-[#94A3B8] truncate">See the risks early</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2.5 py-4 space-y-0.5">
        {!collapsed && (
          <p className="text-[10px] uppercase tracking-[0.22em] text-[#475569] px-3 mb-2">Workspace</p>
        )}
        {mainNav.map((item) => (
          <NavItem key={item.to} {...item} collapsed={collapsed} />
        ))}

        <div className="my-5 mx-1 border-t border-[rgba(59,130,246,0.08)]" />

        {!collapsed && (
          <p className="text-[10px] uppercase tracking-[0.22em] text-[#475569] px-3 mt-5 mb-3">Reports</p>
        )}
        {secondaryNav.map((item) => (
          <NavItem key={item.to} {...item} collapsed={collapsed} />
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-2.5 py-4 border-t border-[rgba(59,130,246,0.08)] space-y-1 flex-shrink-0">
        <button
          onClick={logout}
          title={collapsed ? 'Logout' : undefined}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-[#94A3B8] hover:text-red-400 hover:bg-red-500/5 border border-transparent hover:border-red-500/15 transition-all text-sm font-medium ${collapsed ? 'justify-center' : ''}`}
        >
          <ArrowRightStartOnRectangleIcon className="h-[18px] w-[18px] flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>

        <button
          onClick={onToggle}
          className={`hidden md:flex w-full items-center gap-3 px-3 py-2 rounded-xl text-[#475569] hover:text-[#94A3B8] hover:bg-white/[0.04] transition-all text-xs ${collapsed ? 'justify-center' : ''}`}
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

      {/* Mobile close */}
      <button
        className="md:hidden absolute top-4 right-3 text-[#94A3B8] hover:text-white p-1"
        onClick={onToggle}
        aria-label="Close sidebar"
      >
        ✕
      </button>
    </aside>
  );
};

export default Sidebar;
