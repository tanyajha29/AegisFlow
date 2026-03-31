import React, { useState } from 'react';
import Sidebar from './Sidebar.jsx';
import Topbar from './Topbar.jsx';
import BackgroundFX from './BackgroundFX.jsx';

const Layout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-[#0B1220] cyber-grid">
      <BackgroundFX />
      {/* Sidebar — fixed height, never scrolls */}
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      {/* Main area — scrolls independently */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar onToggleSidebar={() => setCollapsed(!collapsed)} />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-6 py-7 md:px-10 md:py-8 space-y-6 animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
