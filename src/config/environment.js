/**
 * Configuración de entorno para PsiChat
 * Maneja diferentes configuraciones según el entorno
 */

const config = {
  // Configuración base
  base: {
    appName: 'PsiChat',
    version: '1.0.0',
    description: 'Chatbot emocional y análisis de comunicación educativa'
  },

  // Configuración de desarrollo
  development: {
    apiBaseUrl: 'http://127.0.0.1:8000',
    logLevel: 'debug',
    enableDebugTools: true,
    mockData: true
  },

  // Configuración de producción
  production: {
    apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'https://api.psichat.edu',
    logLevel: 'error',
    enableDebugTools: false,
    mockData: false
  },

  // Configuración de testing
  test: {
    apiBaseUrl: 'http://localhost:8000',
    logLevel: 'warn',
    enableDebugTools: false,
    mockData: true
  }
};

// Determinar el entorno actual
const environment = process.env.NODE_ENV || 'development';

// Exportar configuración del entorno actual
export const currentConfig = {
  ...config.base,
  ...config[environment],
  environment
};

// Configuración específica por entorno
export const isDevelopment = environment === 'development';
export const isProduction = environment === 'production';
export const isTest = environment === 'test';

// Configuración de API
export const apiConfig = {
  baseURL: currentConfig.apiBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// Configuración de logging
export const loggingConfig = {
  level: currentConfig.logLevel,
  enableConsole: isDevelopment,
  enableRemote: isProduction
};

// Configuración de características
export const featureFlags = {
  enableNotifications: true,
  enableRealTimeChat: isProduction,
  enableAnalytics: isProduction,
  enableErrorReporting: isProduction,
  enablePerformanceMonitoring: isProduction
};

export default currentConfig; 