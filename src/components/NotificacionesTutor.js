import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { notificationService } from '../services/api';
import {
  FaBell,
  FaExclamationTriangle,
  FaInfoCircle,
  FaBullhorn,
  FaChartBar,
  FaSyncAlt,
  FaCheck,
  FaTrash,
  FaUser,
  FaSpinner,
  FaEnvelopeOpenText,
  FaTools,
  FaLightbulb,
  FaTimes,
} from 'react-icons/fa';
import './NotificacionesTutor.css';

const NotificacionesTutor = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [filteredNotifications, setFilteredNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    urgency: 'all',
    status: 'all',
    type: 'all'
  });
  const [stats, setStats] = useState({
    total: 0,
    unread: 0,
    critical: 0,
    high: 0
  });

  useEffect(() => {
    if (user) {
      loadNotifications();
    }
  }, [user]);

  useEffect(() => {
    applyFilters();
  }, [notifications, filters]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationService.getTutorNotifications();
      setNotifications(response);
      calculateStats(response);
    } catch (err) {
      console.error('Error cargando notificaciones:', err);
      setError('Error al cargar las notificaciones');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (notifs) => {
    const stats = {
      total: notifs.length,
      unread: notifs.filter(n => !n.leida).length,
      critical: notifs.filter(n => n.urgencia === 'critical').length,
      high: notifs.filter(n => n.urgencia === 'high').length
    };
    setStats(stats);
  };

  const applyFilters = () => {
    let filtered = [...notifications];

    if (filters.urgency !== 'all') {
      filtered = filtered.filter(n => n.urgencia === filters.urgency);
    }

    if (filters.status !== 'all') {
      filtered = filtered.filter(n => 
        filters.status === 'unread' ? !n.leida : n.leida
      );
    }

    if (filters.type !== 'all') {
      filtered = filtered.filter(n => n.tipo === filters.type);
    }

    setFilteredNotifications(filtered);
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificationService.markTutorNotificationAsRead(notificationId);
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId ? { ...n, leida: true } : n
        )
      );
    } catch (err) {
      console.error('Error marcando notificación como leída:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      // Asumiendo que el backend tiene un endpoint para marcar todas las notificaciones como leídas
      // Si no, se podría iterar y llamar a markAsRead para cada una
      await notificationService.markAllTutorNotificationsAsRead(); // Esta función no existe, la añadiré a api.js
      setNotifications(prev => 
        prev.map(n => ({ ...n, leida: true }))
      );
    } catch (err) {
      console.error('Error marcando todas las notificaciones:', err);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      // Asumiendo que el backend tiene un endpoint para eliminar notificaciones
      await notificationService.deleteTutorNotification(notificationId); // Esta función no existe, la añadiré a api.js
      setNotifications(prev => 
        prev.filter(n => n.id !== notificationId)
      );
    } catch (err) {
      console.error('Error eliminando notificación:', err);
    }
  };

  const getUrgencyIcon = (urgency) => {
    switch (urgency) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '📢';
      case 'low':
        return 'ℹ️';
      default:
        return '📌';
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'critical':
        return '#e53e3e';
      case 'high':
        return '#d69e2e';
      case 'medium':
        return '#3182ce';
      case 'low':
        return '#38a169';
      default:
        return '#718096';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'alert':
        return '🔔';
      case 'intervention':
        return '🎯';
      case 'analysis':
        return '📊';
      case 'system':
        return '⚙️';
      default:
        return '📌';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 60) {
      return `Hace ${minutes} min`;
    } else if (hours < 24) {
      return `Hace ${hours} h`;
    } else {
      return `Hace ${days} días`;
    }
  };

  if (loading) {
    return (
      <div className="notifications-container">
        <div className="loading-container">
          <div className="spinner">⏳</div>
          <p>Cargando notificaciones...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="notifications-container">
        <div className="error-container">
          <p>❌ {error}</p>
          <button onClick={loadNotifications}>Reintentar</button>
        </div>
      </div>
    );
  }

  return (
    <div className="notifications-container">
      {/* Header */}
      <div className="notifications-header">
        <div className="header-left">
          <h1><FaBell /> Notificaciones</h1>
          <p>Gestiona las alertas y notificaciones del sistema</p>
        </div>
        <div className="header-actions">
          <button 
            className="mark-all-read-btn"
            onClick={markAllAsRead}
            disabled={stats.unread === 0}
          >
            <FaCheck /> Marcar todas como leídas
          </button>
          <button 
            className="refresh-btn"
            onClick={loadNotifications}
          >
            <FaSyncAlt /> Actualizar
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-icon"><FaChartBar /></div>
          <div className="stat-content">
            <h3>Total</h3>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card unread">
          <div className="stat-icon"><FaEnvelopeOpenText /></div>
          <div className="stat-content">
            <h3>No leídas</h3>
            <div className="stat-value">{stats.unread}</div>
          </div>
        </div>
        <div className="stat-card critical">
          <div className="stat-icon"><FaExclamationTriangle /></div>
          <div className="stat-content">
            <h3>Críticas</h3>
            <div className="stat-value">{stats.critical}</div>
          </div>
        </div>
        <div className="stat-card high">
          <div className="stat-icon"><FaBell /></div>
          <div className="stat-content">
            <h3>Altas</h3>
            <div className="stat-value">{stats.high}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Urgencia:</label>
          <select 
            value={filters.urgency}
            onChange={(e) => setFilters(prev => ({ ...prev, urgency: e.target.value }))}
          >
            <option value="all">Todas</option>
            <option value="critical">Crítica</option>
            <option value="high">Alta</option>
            <option value="medium">Media</option>
            <option value="low">Baja</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Estado:</label>
          <select 
            value={filters.status}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
          >
            <option value="all">Todas</option>
            <option value="unread">No leídas</option>
            <option value="read">Leídas</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Tipo:</label>
          <select 
            value={filters.type}
            onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
          >
            <option value="all">Todos</option>
            <option value="alert">Alerta</option>
            <option value="intervention">Intervención</option>
            <option value="analysis">Análisis</option>
            <option value="system">Sistema</option>
          </select>
        </div>
      </div>

      {/* Notifications List */}
      <div className="notifications-list">
        {filteredNotifications.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon"><FaBell /></div>
            <h3>No hay notificaciones</h3>
            <p>No se encontraron notificaciones con los filtros aplicados</p>
          </div>
        ) : (
          filteredNotifications.map(notification => (
            <div 
              key={notification.id} 
              className={`notification-card ${!notification.leida ? 'unread' : ''} ${notification.urgencia}`}
            >
              <div className="notification-header">
                <div className="notification-meta">
                  <span className="urgency-icon">
                    {getUrgencyIcon(notification.urgencia)}
                  </span>
                  <span className="type-icon">
                    {getTypeIcon(notification.tipo)}
                  </span>
                  <span className="notification-time">
                    {formatTime(notification.timestamp)}
                  </span>
                </div>
                <div className="notification-actions">
                  {!notification.leida && (
                    <button 
                      className="mark-read-btn"
                      onClick={() => markAsRead(notification.id)}
                      title="Marcar como leída"
                    >
                      <FaCheck />
                    </button>
                  )}
                  <button 
                    className="delete-btn"
                    onClick={() => deleteNotification(notification.id)}
                    title="Eliminar"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
              
              <div className="notification-content">
                <h4 className="notification-title">{notification.titulo}</h4>
                <p className="notification-message">{notification.mensaje}</p>
                
                {notification.estudiante && (
                  <div className="student-info">
                    <span className="student-avatar"><FaUser /></span>
                    <span className="student-name">{notification.estudiante.nombre}</span>
                    {notification.estudiante.curso && (
                      <span className="student-course">{notification.estudiante.curso}</span>
                    )}
                  </div>
                )}
                
                {notification.datos_adicionales && (
                  <div className="additional-data">
                    <details>
                      <summary>Ver detalles adicionales</summary>
                      <pre>{JSON.stringify(notification.datos_adicionales, null, 2)}</pre>
                    </details>
                  </div>
                )}
              </div>
              
              <div className="notification-footer">
                <span 
                  className="urgency-badge"
                  style={{ backgroundColor: `${getUrgencyColor(notification.urgencia)}20`, color: getUrgencyColor(notification.urgencia) }}
                >
                  {notification.urgencia.toUpperCase()}
                </span>
                <span className="type-badge">{notification.tipo}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default NotificacionesTutor; 