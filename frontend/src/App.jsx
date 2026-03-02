import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext.jsx';
import Navbar from './components/Navbar.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Dashboard from './pages/Dashboard.jsx';
import ScanReport from './pages/ScanReport.jsx';

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const App = () => {
  const { user } = useAuth();
  return (
    <div className="min-h-screen bg-darker text-slate-200">
      {user && <Navbar />}
      <div className={user ? "pt-16" : ""}>
        {/* Adds top padding for fixed navbar if logged in */}
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/report/:id" element={
            <ProtectedRoute>
              <ScanReport />
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </div>
  );
};

export default App;
