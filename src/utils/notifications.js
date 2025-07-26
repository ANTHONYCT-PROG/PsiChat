/**
 * Sistema de notificaciones para PsiChat
 * Reemplaza alerts con notificaciones elegantes
 */

class NotificationManager {
  constructor() {
    this.notifications = [];
    this.nextId = 1;
  }

  // Tipos de notificación
  static TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
  };

  // Crear notificación
  create(type, message, title = null, duration = 5000) {
    const notification = {
      id: this.nextId++,
      type,
      message,
      title,
      timestamp: new Date(),
      duration
    };

    this.notifications.push(notification);
    this.render(notification);

    // Auto-remover después del tiempo especificado
    if (duration > 0) {
      setTimeout(() => {
        this.remove(notification.id);
      }, duration);
    }

    return notification.id;
  }

  // Métodos de conveniencia
  success(message, title = 'Éxito') {
    return this.create(NotificationManager.TYPES.SUCCESS, message, title);
  }

  error(message, title = 'Error') {
    return this.create(NotificationManager.TYPES.ERROR, message, title, 8000);
  }

  warning(message, title = 'Advertencia') {
    return this.create(NotificationManager.TYPES.WARNING, message, title);
  }

  info(message, title = 'Información') {
    return this.create(NotificationManager.TYPES.INFO, message, title);
  }

  // Remover notificación
  remove(id) {
    const notification = document.getElementById(`notification-${id}`);
    if (notification) {
      notification.classList.add('notification-fade-out');
      setTimeout(() => {
        notification.remove();
        this.notifications = this.notifications.filter(n => n.id !== id);
      }, 300);
    }
  }

  // Renderizar notificación
  render(notification) {
    const container = this.getOrCreateContainer();
    
    const notificationElement = document.createElement('div');
    notificationElement.id = `notification-${notification.id}`;
    notificationElement.className = `notification notification-${notification.type}`;
    
    const icon = this.getIcon(notification.type);
    const title = notification.title ? `<div class="notification-title">${notification.title}</div>` : '';
    
    notificationElement.innerHTML = `
      <div class="notification-content">
        <div class="notification-icon">${icon}</div>
        <div class="notification-body">
          ${title}
          <div class="notification-message">${notification.message}</div>
        </div>
        <button class="notification-close" onclick="window.notificationManager.remove(${notification.id})">
          ×
        </button>
      </div>
    `;

    container.appendChild(notificationElement);
    
    // Animación de entrada
    setTimeout(() => {
      notificationElement.classList.add('notification-show');
    }, 10);
  }

  // Obtener o crear contenedor
  getOrCreateContainer() {
    let container = document.getElementById('notification-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'notification-container';
      container.className = 'notification-container';
      document.body.appendChild(container);
    }
    return container;
  }

  // Obtener icono según tipo
  getIcon(type) {
    const icons = {
      [NotificationManager.TYPES.SUCCESS]: '✓',
      [NotificationManager.TYPES.ERROR]: '✕',
      [NotificationManager.TYPES.WARNING]: '⚠',
      [NotificationManager.TYPES.INFO]: 'ℹ'
    };
    return icons[type] || 'ℹ';
  }

  // Limpiar todas las notificaciones
  clear() {
    const container = document.getElementById('notification-container');
    if (container) {
      container.innerHTML = '';
    }
    this.notifications = [];
  }
}

// Instancia global
const notificationManager = new NotificationManager();

// Hacer disponible globalmente para uso en componentes
if (typeof window !== 'undefined') {
  window.notificationManager = notificationManager;
}

export default notificationManager; 