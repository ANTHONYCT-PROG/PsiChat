/**
 * Sistema de logging profesional para PsiChat
 * Reemplaza console.log y alerts con un sistema estructurado
 */

class Logger {
  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.logLevel = this.isDevelopment ? 'debug' : 'error';
  }

  // Niveles de log
  static LEVELS = {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3
  };

  shouldLog(level) {
    return Logger.LEVELS[level.toUpperCase()] <= Logger.LEVELS[this.logLevel.toUpperCase()];
  }

  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    
    if (data) {
      return `${prefix} ${message}`, data;
    }
    return `${prefix} ${message}`;
  }

  error(message, error = null) {
    if (this.shouldLog('error')) {
      console.error(this.formatMessage('error', message), error || '');
    }
  }

  warn(message, data = null) {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', message), data || '');
    }
  }

  info(message, data = null) {
    if (this.shouldLog('info')) {
      console.info(this.formatMessage('info', message), data || '');
    }
  }

  debug(message, data = null) {
    if (this.shouldLog('debug')) {
      console.log(this.formatMessage('debug', message), data || '');
    }
  }

  // Método para logs de autenticación
  auth(message, data = null) {
    this.info(`[AUTH] ${message}`, data);
  }

  // Método para logs de API
  api(message, data = null) {
    this.info(`[API] ${message}`, data);
  }

  // Método para logs de análisis
  analysis(message, data = null) {
    this.info(`[ANALYSIS] ${message}`, data);
  }

  // Método para logs de chat
  chat(message, data = null) {
    this.info(`[CHAT] ${message}`, data);
  }
}

// Instancia singleton
const logger = new Logger();

export default logger; 