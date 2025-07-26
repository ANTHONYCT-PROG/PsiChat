import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';
import logger from '../utils/logger';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
      checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
        logger.auth('Estado de autenticación verificado', { userId: userData.id });
      }
    } catch (error) {
      logger.error('Error al verificar estado de autenticación', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authService.login(email, password);
      const { token, user: userData } = response;
      
      localStorage.setItem('token', token);
      setUser(userData);
      setIsAuthenticated(true);
      setError(null);
      
      logger.auth('Login exitoso', { userId: userData.id, email });
      return userData;
    } catch (error) {
      logger.error('Error en login', error);
      setError(error.response?.data?.detail || 'Error en el inicio de sesión');
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      const { token, user: newUser } = response;
      
      localStorage.setItem('token', token);
      setUser(newUser);
      setIsAuthenticated(true);
      setError(null);
      
      logger.auth('Registro exitoso', { userId: newUser.id, email: newUser.email });
      return newUser;
    } catch (error) {
      logger.error('Error en registro', error);
      setError(error.response?.data?.detail || 'Error en el registro');
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    logger.auth('Logout realizado');
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const clearError = () => {
    setError(null);
  };

  const updatePassword = async (oldPassword, newPassword) => {
    try {
      await authService.changePassword(oldPassword, newPassword);
      logger.auth('Contraseña actualizada exitosamente', { userId: user?.id });
    } catch (error) {
      logger.error('Error al cambiar contraseña', error);
      throw error;
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    updateUser,
    clearError,
    updatePassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 