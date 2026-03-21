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
} from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext.jsx';

const navItems = [
  { to: '/app', label: 'Dashboard', icon: HomeModernIcon },
  { to: '/app/scan', label: 'Scan Code', icon: CodeBracketSquareIcon },
  { to: '/app/results', label: 'Scan Results', icon: ArrowUpOnSquareStackIcon },
  { to: '/app/history', label: 'Scan History', icon: ClockIcon },
  { to: '/app/reports', label: 'Security Reports', icon: DocumentTextIcon },
  { to: '/app/settings', label: 'Settings', icon: Cog6ToothIcon },
];

const Sidebar = ({ collapsed, onToggle }) => {
  const { logout } = useAuth();

  return (
    <aside
      className={`fixed md:static z-30 h-screen md:h-auto w-72 md:w-72 glass-card bg-[rgba(15,23,42,0.9)] border border-[rgba(59,130,246,0.2)] backdrop-blur-2xl transition-all duration-300 ${
        collapsed ? '-translate-x-full md:translate-x-0' : 'translate-x-0'
      }`}
    >
      <div className="flex items-center justify-between px-5 py-5">
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-cyber to-accent flex items-center justify-center shadow-glow">
            <EyeIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <p className="text-white font-semibold">DristiScan</p>
            <p className="text-xs text-slate-400">See the risks early</p>
          </div>
        </div>
        <button className="md:hidden text-slate-400" onClick={onToggle}>✕</button>
      </div>

      <nav className="px-3 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition hover:bg-white/5 ${
                isActive ? 'bg-white/10 border border-border text-white' : 'text-slate-300'
              }`
            }
          >
            <Icon className="h-5 w-5" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-6 mt-auto">
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 transition border border-border"
        >
          <ArrowRightStartOnRectangleIcon className="h-5 w-5" />
          Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
