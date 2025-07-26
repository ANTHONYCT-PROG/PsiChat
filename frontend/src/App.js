import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { showNotification } from './utils/notifications';
import logger from './utils/logger';
import { debounce } from './utils/performance';
import ErrorBoundary from './components/ErrorBoundary'; // Importar el ErrorBoundary personalizado

// Lazy loading de componentes para mejor rendimiento
const Login = lazy(() => import('./components/Login'));
const StudentDashboard = lazy(() => import('./components/StudentDashboard'));
const ChatPrincipal = lazy(() => import('./components/ChatPrincipal'));
const AnalisisEmocional = lazy(() => import('./components/AnalisisEmocional'));
const AnalisisProfundo = lazy(() => import('./components/AnalisisProfundo'));
const PanelTutor = lazy(() => import('./components/PanelTutor'));
const ChatDirecto = lazy(() => import('./components/ChatDirecto'));
const Configuracion = lazy(() => import('./components/Configuracion'));
const PerfilUsuario = lazy(() => import('./components/PerfilUsuario'));
const DashboardTutor = lazy(() => import('./components/DashboardTutor'));
const CambiarContrasena = lazy(() => import('./components/CambiarContrasena'));

import './App.css';

// Componente de carga
const LoadingSpinner = () => (
  <div className="loading-container">
    <div className="spinner"></div>
    <p>Cargando...</p>
  </div>
);

// Componente para proteger rutas con roles específicos
const ProtectedRoute = ({ children, allowedRoles = [], requiredPermissions = [] }) => {
  const { user, isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (!isAuthenticated) {
    showNotification.warning('Debes iniciar sesión para acceder a esta página');
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.rol)) {
    showNotification.error('No tienes permisos para acceder a esta página');
    return <Navigate to="/" replace />;
  }
  
  if (requiredPermissions.length > 0) {
    const userPermissions = user?.permisos || [];
    const hasAllPermissions = requiredPermissions.every(permission => 
      userPermissions.includes(permission)
    );
    
    if (!hasAllPermissions) {
      showNotification.error('No tienes los permisos necesarios');
      return <Navigate to="/" replace />;
    }
  }
  
  return children;
};

// Componente principal de la aplicación
const AppContent = () => {

  // Optimización: Debounce para eventos de resize
  const handleResize = debounce(() => {
    logger.debug('Ventana redimensionada');
  }, 250);

  React.useEffect(() => {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [handleResize]);

  return (
    <Router>
      <ErrorBoundary>
      <div className="App">
          <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Ruta pública */}
          <Route path="/login" element={<Login />} />
          
          {/* Rutas protegidas para estudiantes */}
          <Route 
            path="/" 
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <StudentDashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/chat" 
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <ChatPrincipal />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/analisis" 
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <AnalisisEmocional />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/analisis-profundo" 
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <AnalisisProfundo />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/chat-directo/:studentId" 
            element={
              <ProtectedRoute allowedRoles={['estudiante']}>
                <ChatDirecto />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/configuracion" 
            element={
              <ProtectedRoute>
                <Configuracion />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/perfil" 
            element={
              <ProtectedRoute>
                <PerfilUsuario />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/cambiar-contrasena" 
            element={
              <ProtectedRoute>
                <CambiarContrasena />
              </ProtectedRoute>
            } 
          />
          
          {/* Rutas para tutores */}
          <Route 
            path="/tutor" 
                element={
                  <ProtectedRoute allowedRoles={['tutor']}>
                    <DashboardTutor />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/tutor/panel" 
            element={
              <ProtectedRoute allowedRoles={['tutor']}>
                <PanelTutor />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/tutor/chat/:studentId" 
            element={
              <ProtectedRoute allowedRoles={['tutor']}>
                <ChatDirecto />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirección por defecto */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
          </Suspense>
      </div>
      </ErrorBoundary>
    </Router>
  );
};

// Componente principal con providers
const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App; 