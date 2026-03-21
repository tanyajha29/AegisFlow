import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';

import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Scan from './pages/Scan.jsx';
import Results from './pages/Results.jsx';
import Reports from './pages/Reports.jsx';
import History from './pages/History.jsx';
import Settings from './pages/Settings.jsx';
import Layout from './components/Layout.jsx';
import LandingPage from './pages/page';

const Protected = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
};

const App = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-navy text-slate-100">
      <Routes>
        <Route path="/" element={user ? <Navigate to="/app" replace /> : <LandingPage />} />
        <Route path="/login" element={user ? <Navigate to="/app" replace /> : <Login />} />
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
                  <Route path="history" element={<History />} />
                  <Route path="settings" element={<Settings />} />
                  <Route path="*" element={<Navigate to="/app" replace />} />
                </Routes>
              </Layout>
            </Protected>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
};

export default App;
