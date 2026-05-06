import './index.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { AuthProvider } from './features/auth/AuthProvider';
import PrivateRoute from './features/auth/PrivateRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import App from './App';
import SessionPage from './pages/SessionPage';
import AchievementsPage from './pages/AchievementsPage';
import ProfilePage from './pages/ProfilePage';
import SessionDetailPage from './pages/SessionDetailPage';
import CommunityPage from './pages/CommunityPage';
import AppLayout from './components/AppLayout';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* A página inicial controla a Navbar internamente para ocultá-la durante a sessão ativa. */}
          <Route path="/" element={<App />} />
          <Route element={<AppLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <DashboardPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/session"
              element={
                <PrivateRoute>
                  <SessionPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/session/:id"
              element={
                <PrivateRoute>
                  <SessionDetailPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/achievements"
              element={
                <PrivateRoute>
                  <AchievementsPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <PrivateRoute>
                  <ProfilePage />
                </PrivateRoute>
              }
            />
            <Route path="/community" element={<CommunityPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>
);
