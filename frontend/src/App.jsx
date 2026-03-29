import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';

import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Scan from './pages/Scan.jsx';
import Results from './pages/Results.jsx';
import Reports from './pages/Reports.jsx';
import ReportDetails from './pages/ReportDetails.jsx';
import History from './pages/History.jsx';
import Settings from './pages/Settings.jsx';
import Layout from './components/Layout.jsx';
import LandingPage from './pages/page';

const Protected = ({ children }) => {
  // TEMPORARILY REMOVED AUTH CHECK FOR UI TESTING
  return children;
};

const App = () => {
  // TEMPORARILY REMOVED AUTH CHECK FOR UI TESTING
  const user = { id: '1', email: 'test@example.com' };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 text-slate-100">
      <Routes>
        <Route path="/" element={<Navigate to="/app" replace />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/app/*"
          element={
            <Protected>
              <Layout>
                <Routes>
                  <Route index element={<Dashboard />} />
                  <Route path="scan" element={<Scan />} />
                  <Route path="results" element={<Results />} />
                  <Route path="reports" element={<Reports />} />
                  <Route path="reports/:scanId" element={<ReportDetails />} />
                  <Route path="history" element={<History />} />
                  <Route path="settings" element={<Settings />} />
                  <Route path="*" element={<Navigate to="/app" replace />} />
                </Routes>
              </Layout>
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/app" replace />} />
      </Routes>
    </div>
  );
};

export default App;
