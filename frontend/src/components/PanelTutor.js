import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { userService, notificationService } from '../services/api';
import logger from '../utils/logger';
import { showNotification } from '../utils/notifications';
import { 
  FaBell,
  FaUser, 
  FaSignOutAlt,
  FaExclamationTriangle,
  FaComments,
  FaChartBar,
  FaUsers,
  FaCog,
  FaEye,
  FaCheck,
  FaTimes,
  FaSpinner,
  FaBrain,
} from 'react-icons/fa';
import NotificacionesTutor from './NotificacionesTutor';
import './PanelTutor.css';

const PanelTutor = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [interventionMessage, setInterventionMessage] = useState('');
  const [sendingIntervention, setSendingIntervention] = useState(false);
  const [filters, setFilters] = useState({
    emotion: 'all',
    urgency: 'all',
    reviewed: 'all',
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadAlerts(),
        loadStats(),
        loadStudents(),
      ]);
      logger.info('Datos iniciales del panel de tutor cargados');
    } catch (error) {
      logger.error('Error al cargar datos iniciales del panel', error);
      showNotification.error('Error al cargar los datos del panel');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    const tutorStats = await userService.getTutorStats();
    setStats(tutorStats);
  };

  const loadAlerts = async () => {
    const alertsData = await userService.getAlerts();
    setAlerts(alertsData);
  };

  const loadStudentConversation = async (studentId) => {
      const conversation = await userService.getStudentConversation(studentId);
      return conversation;
  };

  const applyFilters = () => {
    // Implementar lógica de filtrado
  };

  const handleViewDetail = (alert) => {
    setSelectedAlert(alert);
  };

  const handleIntervene = (alert) => {
    setSelectedAlert(alert);
    setInterventionMessage('');
  };

  const handleSendIntervention = async () => {
    if (!interventionMessage.trim() || !selectedAlert) return;

      setSendingIntervention(true);
    try {
      await userService.sendIntervention(selectedAlert.student_id, interventionMessage);
      showNotification.success('Intervención enviada correctamente');
      setInterventionMessage('');
      setSelectedAlert(null);
      logger.info('Intervención enviada', { studentId: selectedAlert.student_id });
    } catch (error) {
      logger.error('Error al enviar intervención', error);
      showNotification.error('Error al enviar la intervención');
    } finally {
      setSendingIntervention(false);
    }
  };

  const handleMarkAsReviewed = async (alertId) => {
    try {
      await userService.markAlertAsReviewed(alertId);
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, reviewed: true } : alert
      ));
      showNotification.success('Alerta marcada como revisada');
      logger.info('Alerta marcada como revisada', { alertId });
    } catch (error) {
      logger.error('Error al marcar alerta como revisada', error);
      showNotification.error('Error al marcar la alerta');
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'alta': return '#e53e3e';
      case 'media': return '#d69e2e';
      default: return '#38a169';
    }
  };

  const getUrgencyLabel = (urgency) => {
    switch (urgency) {
      case 'alta': return 'Alta';
      case 'media': return 'Media';
      default: return 'Baja';
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString('es-ES');
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Ahora mismo';
    if (diffInMinutes < 60) return `Hace ${diffInMinutes} min`;
    if (diffInMinutes < 1440) return `Hace ${Math.floor(diffInMinutes / 60)}h`;
    return `Hace ${Math.floor(diffInMinutes / 1440)}d`;
  };

  const loadStudents = async () => {
    const studentsData = await userService.getStudents();
    setStudents(studentsData);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="tutor-container">
        <div className="loading-container">
          <FaSpinner className="spinner" />
          <p>Cargando panel de tutor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tutor-container">
      {/* Header */}
      <div className="tutor-header">
        <div className="header-left">
          <div className="logo-section">
            <FaBrain className="logo-icon" />
            <h1>Panel de Tutor</h1>
          </div>
        </div>
        
        <div className="header-center">
          <div className="filter-section">
            <button className="filter-toggle" onClick={applyFilters}>
              <FaCog />
              Filtros
            </button>
            <div className="filter-controls">
              <select
                value={filters.emotion}
                onChange={(e) => setFilters(prev => ({ ...prev, emotion: e.target.value }))}
                className="filter-select"
              >
                <option value="all">Todas las emociones</option>
                <option value="tristeza">Tristeza</option>
                <option value="ansiedad">Ansiedad</option>
                <option value="frustración">Frustración</option>
              </select>
              <select
                value={filters.urgency}
                onChange={(e) => setFilters(prev => ({ ...prev, urgency: e.target.value }))}
                className="filter-select"
            >
                <option value="all">Todas las urgencias</option>
                <option value="alta">Alta</option>
                <option value="media">Media</option>
                <option value="baja">Baja</option>
              </select>
            </div>
          </div>
        </div>
        
        <div className="header-right">
          <button 
            className="notifications-btn"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <FaBell />
            {stats.unread_notifications > 0 && (
              <span className="notification-badge">{stats.unread_notifications}</span>
            )}
          </button>
          <button className="profile-btn" onClick={handleLogout}>
            <FaUser />
            <span>{user?.nombre}</span>
            <FaSignOutAlt />
          </button>
                </div>
              </div>
              
      {/* Main Content */}
      <div className="tutor-main">
        <div className="alerts-container">
          <div className="alerts-header">
            <h2>Alertas Emocionales</h2>
            <div className="alerts-stats">
              <div className="stat-item">
                <FaExclamationTriangle className="stat-icon critical" />
                <span>{stats.critical_alerts || 0} Críticas</span>
              </div>
              <div className="stat-item">
                <FaExclamationTriangle className="stat-icon warning" />
                <span>{stats.warning_alerts || 0} Advertencias</span>
              </div>
              <div className="stat-item">
                <FaExclamationTriangle className="stat-icon info" />
                <span>{stats.info_alerts || 0} Informativas</span>
              </div>
            </div>
          </div>

          <div className="alerts-list">
            {alerts.length === 0 ? (
                <div className="no-alerts">
                <p>No hay alertas pendientes</p>
                </div>
              ) : (
              alerts.map((alert) => (
                  <div 
                    key={alert.id} 
                    className={`alert-card ${alert.reviewed ? 'reviewed' : ''}`}
                  >
                    <div className="alert-student">
                    <div className="student-avatar">
                      <FaUser />
                    </div>
                      <div className="student-info">
                      <h3>{alert.student_name}</h3>
                      <p>{alert.student_email}</p>
                    </div>
                  </div>

                    <div className="alert-content">
                      <div className="message-preview">
                      <p>&ldquo;{alert.message_preview}&rdquo;</p>
                      </div>
                      <div className="alert-emotion">
                      <span className="emotion-icon"><FaBrain /></span>
                      <span className="emotion-name">{alert.emotion}</span>
                    </div>
                      <div 
                        className="urgency-badge"
                        style={{ backgroundColor: getUrgencyColor(alert.urgency) }}
                      >
                        {getUrgencyLabel(alert.urgency)}
                      </div>
                    </div>

                    <div className="alert-actions">
                      <button 
                      className="btn-primary"
                      onClick={() => handleViewDetail(alert)}
                    >
                      <FaEye />
                      Ver Detalle
                    </button>
                    <button
                      className="btn-primary"
                        onClick={() => handleIntervene(alert)}
                      >
                      <FaComments />
                      Intervenir
                    </button>
                    {!alert.reviewed && (
                      <button
                        className="btn-primary"
                        onClick={() => handleMarkAsReviewed(alert.id)}
                      >
                        <FaCheck />
                        Marcar Revisada
                      </button>
                    )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
      </div>

      {/* Notifications Panel */}
      {showNotifications && (
        <NotificacionesTutor onClose={() => setShowNotifications(false)} />
      )}

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="modal-overlay" onClick={() => setSelectedAlert(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-student-info">
                <div className="student-avatar-large">
                  <FaUser />
                </div>
                <div>
                  <h2>{selectedAlert.student_name}</h2>
                  <p>{selectedAlert.student_email}</p>
                </div>
              </div>
              <button className="close-btn" onClick={() => setSelectedAlert(null)}>
                <FaTimes />
              </button>
            </div>

            <div className="modal-body">
              <div className="conversation-section">
                <h3>Conversación Reciente</h3>
                <div className="conversation-container">
                  {/* Aquí se mostraría la conversación */}
                  <p>Conversación del estudiante con PsiChat...</p>
                </div>
              </div>

              <div className="intervention-section">
                <h3>Enviar Intervención</h3>
                <div className="intervention-input-container">
                  <textarea
                    className="intervention-textarea"
                    value={interventionMessage}
                    onChange={(e) => setInterventionMessage(e.target.value)}
                    placeholder="Escribe tu mensaje de intervención..."
                    rows="4"
                  />
                  <button 
                    className="send-btn"
                    onClick={handleSendIntervention}
                    disabled={!interventionMessage.trim() || sendingIntervention}
                  >
                    {sendingIntervention ? <FaSpinner /> : <FaComments />}
                    {sendingIntervention ? 'Enviando...' : 'Enviar Intervención'}
                  </button>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn-success"
                onClick={() => handleMarkAsReviewed(selectedAlert.id)}
              >
                <FaCheck />
                Marcar como Revisada
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PanelTutor;

export default PanelTutor;
