import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { showNotification } from '../utils/notifications';
import logger from '../utils/logger';
import { FaUser, FaLock, FaEye, FaEyeSlash, FaGoogle } from 'react-icons/fa';
import './Login.css';

const Login = () => {
  const { login, register, error, clearError } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isLoginMode, setIsLoginMode] = useState(true);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    if (error) clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLoginMode) {
        await login(formData.email, formData.password);
        logger.auth('Login exitoso', { email: formData.email });
        showNotification.success('¡Bienvenido de vuelta!');
      } else {
        await register({ email: formData.email, password: formData.password, name: formData.name });
        logger.auth('Registro exitoso', { email: formData.email });
        showNotification.success('¡Cuenta creada exitosamente!');
      }
    } catch (error) {
      logger.error('Error en autenticación', error);
      showNotification.error(error.message || 'Error en la autenticación');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setFormData({ email: '', password: '', name: '' });
    clearError();
  };

  const handleSSO = () => {
    showNotification.info('Funcionalidad de SSO en desarrollo');
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();
    showNotification.info('Funcionalidad de recuperación en desarrollo');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-container">
            <div className="logo-icon">🧠</div>
          </div>
          <h1>{isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta'}</h1>
          <p className="subtitle">
            {isLoginMode 
              ? 'Accede a tu cuenta de PsiChat' 
              : 'Únete a PsiChat y comienza tu viaje emocional'
            }
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              <FaUser className="input-icon" />
              Email
            </label>
            <input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className="form-input"
              placeholder="tu@email.com"
              required
            />
          </div>

          {!isLoginMode && (
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                <FaUser className="input-icon" />
                Nombre
              </label>
              <input
                id="name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Tu nombre completo"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              <FaLock className="input-icon" />
              Contraseña
            </label>
            <div className="password-input-container">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="password-input"
                placeholder="Tu contraseña"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={togglePasswordVisibility}
                aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className={`login-btn ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? 'Procesando...' : (isLoginMode ? 'Iniciar Sesión' : 'Crear Cuenta')}
          </button>
        </form>

        <div className="login-footer">
          <button className="sso-btn" onClick={handleSSO}>
            <FaGoogle />
            Continuar con Google
          </button>

          <div className="login-links">
            <button
              type="button"
              onClick={toggleMode}
              className="link-btn"
            >
              {isLoginMode 
                ? '¿No tienes cuenta? Regístrate' 
                : '¿Ya tienes cuenta? Inicia sesión'
              }
            </button>
            
            {isLoginMode && (
              <>
                <span className="separator">•</span>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="link-btn"
                >
                  ¿Olvidaste tu contraseña?
                </button>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="message error">
            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login; 