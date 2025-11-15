import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AuditLogs from './pages/AuditLogs';
import EncryptTool from './pages/EncryptTool';
import Navbar from './components/Navbar';
import { getToken, removeToken } from './api/auth';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (token) {
      try {
        // Decode JWT to get user info (simple base64 decode)
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({
          id: parseInt(payload.sub),
          username: payload.username,
          role: payload.role
        });
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Invalid token:', error);
        removeToken();
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    removeToken();
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {isAuthenticated && <Navbar user={user} onLogout={handleLogout} />}
        
        <main className={isAuthenticated ? 'pt-16' : ''}>
          <Routes>
            <Route 
              path="/login" 
              element={
                !isAuthenticated ? 
                <Login onLogin={handleLogin} /> : 
                <Navigate to="/dashboard" replace />
              } 
            />
            
            <Route 
              path="/dashboard" 
              element={
                isAuthenticated ? 
                <Dashboard user={user} /> : 
                <Navigate to="/login" replace />
              } 
            />
            
            <Route 
              path="/audit" 
              element={
                isAuthenticated && user?.role === 'admin' ? 
                <AuditLogs /> : 
                <Navigate to="/dashboard" replace />
              } 
            />
            
            <Route 
              path="/encrypt" 
              element={
                isAuthenticated ? 
                <EncryptTool /> : 
                <Navigate to="/login" replace />
              } 
            />
            
            <Route 
              path="/" 
              element={
                <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;