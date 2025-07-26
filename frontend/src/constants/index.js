/**
 * Constantes centralizadas para PsiChat
 */

// Roles de usuario
export const USER_ROLES = {
  STUDENT: 'estudiante',
  TUTOR: 'tutor',
  ADMIN: 'admin'
};

// Estados de autenticación
export const AUTH_STATUS = {
  AUTHENTICATED: 'authenticated',
  UNAUTHENTICATED: 'unauthenticated',
  LOADING: 'loading'
};

// Tipos de emoción
export const EMOTIONS = {
  JOY: 'alegría',
  SADNESS: 'tristeza',
  ANXIETY: 'ansiedad',
  FRUSTRATION: 'frustración',
  CALM: 'calma',
  DISCOURAGEMENT: 'desánimo'
};

// Colores para emociones
export const EMOTION_COLORS = {
  [EMOTIONS.JOY]: '#38a169',
  [EMOTIONS.SADNESS]: '#3182ce',
  [EMOTIONS.ANXIETY]: '#d69e2e',
  [EMOTIONS.FRUSTRATION]: '#e53e3e',
  [EMOTIONS.CALM]: '#38b2ac',
  [EMOTIONS.DISCOURAGEMENT]: '#805ad5'
};

// Estilos de comunicación
export const COMMUNICATION_STYLES = {
  FORMAL: 'formal',
  INFORMAL: 'informal',
  ASSERTIVE: 'asertivo',
  PASSIVE: 'pasivo',
  AGGRESSIVE: 'agresivo'
};

// Niveles de urgencia
export const URGENCY_LEVELS = {
  HIGH: 'alta',
  MEDIUM: 'media',
  LOW: 'baja'
};

// Colores para urgencia
export const URGENCY_COLORS = {
  [URGENCY_LEVELS.HIGH]: '#e53e3e',
  [URGENCY_LEVELS.MEDIUM]: '#d69e2e',
  [URGENCY_LEVELS.LOW]: '#38a169'
};

// Tipos de notificación
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Tipos de alerta
export const ALERT_TYPES = {
  EMOTIONAL: 'emotional',
  ACADEMIC: 'academic',
  BEHAVIORAL: 'behavioral',
  SYSTEM: 'system'
};

// Estados de mensaje
export const MESSAGE_STATUS = {
  SENT: 'sent',
  DELIVERED: 'delivered',
  READ: 'read',
  FAILED: 'failed'
};

// Configuración de paginación
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  DEFAULT_PAGE: 1
};

// Timeouts
export const TIMEOUTS = {
  API_REQUEST: 10000,
  TYPING_INDICATOR: 3000,
  NOTIFICATION: 5000,
  SESSION: 3600000 // 1 hora
};

// Rutas de la aplicación
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  CHAT: '/chat',
  ANALYSIS: '/analisis',
  DEEP_ANALYSIS: '/analisis-profundo',
  TUTOR: '/tutor',
  PROFILE: '/perfil',
  SETTINGS: '/configuracion',
  CHAT_DIRECT: '/chat-directo'
};

// Configuración de API
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    CURRENT_USER: '/auth/me'
  },
  CHAT: {
    SEND_MESSAGE: '/chat/send',
    HISTORY: '/chat/history',
    CONVERSATION: '/chat/conversation'
  },
  ANALYSIS: {
    ANALYZE: '/analysis/analyze',
    LAST_ANALYSIS: '/analysis/last',
    DEEP_ANALYSIS: '/analysis/deep'
  },
  TUTOR: {
    ALERTS: '/tutor/alerts',
    STUDENTS: '/tutor/students',
    STATS: '/tutor/stats',
    INTERVENTION: '/tutor/intervention'
  }
};

// Configuración de localStorage
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  SETTINGS: 'settings',
  THEME: 'theme',
  LANGUAGE: 'language'
};

// Configuración de temas
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
};

// Configuración de idiomas
export const LANGUAGES = {
  ES: 'es',
  EN: 'en'
};

// Configuración de validación
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD_MIN_LENGTH: 8,
  NAME_MIN_LENGTH: 2,
  MESSAGE_MAX_LENGTH: 1000
};

// Mensajes de error
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Error de conexión. Verifica tu internet.',
  UNAUTHORIZED: 'No tienes permisos para realizar esta acción.',
  NOT_FOUND: 'El recurso solicitado no fue encontrado.',
  VALIDATION_ERROR: 'Los datos ingresados no son válidos.',
  SERVER_ERROR: 'Error del servidor. Inténtalo más tarde.',
  TIMEOUT_ERROR: 'La solicitud tardó demasiado. Inténtalo de nuevo.'
};

// Mensajes de éxito
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Sesión iniciada correctamente.',
  REGISTER_SUCCESS: 'Cuenta creada exitosamente.',
  LOGOUT_SUCCESS: 'Sesión cerrada.',
  SAVE_SUCCESS: 'Cambios guardados correctamente.',
  SEND_SUCCESS: 'Mensaje enviado correctamente.'
};

// Configuración de animaciones
export const ANIMATIONS = {
  DURATION: {
    FAST: 200,
    NORMAL: 300,
    SLOW: 500
  },
  EASING: {
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out'
  }
};

// Configuración de breakpoints
export const BREAKPOINTS = {
  MOBILE: 768,
  TABLET: 1024,
  DESKTOP: 1200
};

// Configuración de gráficos
export const CHART_CONFIG = {
  COLORS: [
    '#667eea',
    '#764ba2',
    '#f093fb',
    '#f5576c',
    '#4facfe',
    '#00f2fe'
  ],
  ANIMATION_DURATION: 1000,
  RESPONSIVE: true
};

export default {
  USER_ROLES,
  AUTH_STATUS,
  EMOTIONS,
  EMOTION_COLORS,
  COMMUNICATION_STYLES,
  URGENCY_LEVELS,
  URGENCY_COLORS,
  NOTIFICATION_TYPES,
  ALERT_TYPES,
  MESSAGE_STATUS,
  PAGINATION,
  TIMEOUTS,
  ROUTES,
  API_ENDPOINTS,
  STORAGE_KEYS,
  THEMES,
  LANGUAGES,
  VALIDATION,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  ANIMATIONS,
  BREAKPOINTS,
  CHART_CONFIG
}; 