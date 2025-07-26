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
  FaUsers,
  FaSpinner,
  FaTachometerAlt,
  FaTrendingUp,
  FaTrendingDown,
  FaGraduationCap,
  FaBrain,
  FaLightbulb,
} from 'react-icons/fa';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import NotificacionesTutor from './NotificacionesTutor';
import './DashboardTutor.css';

const DashboardTutor = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('alerts');

  useEffect(() => {
    loadDashboardData();
  }, [timeRange]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const data = await userService.getDashboardData({ timeRange });
      setDashboardData(data);
      logger.info('Datos del dashboard cargados', { timeRange });
    } catch (error) {
      logger.error('Error al cargar datos del dashboard', error);
      showNotification.error('Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'alerts':
        navigate('/tutor/panel');
        break;
      case 'students':
        navigate('/tutor/estudiantes');
        break;
      case 'reports':
        navigate('/tutor/reportes');
        break;
      case 'analytics':
        navigate('/tutor/estadisticas');
        break;
      default:
        break;
    }
  };

  if (loading) {
    return (
      <div className="dashboard-tutor-container">
        <div className="loading-container">
          <FaSpinner className="spinner" />
          <p>Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="dashboard-tutor-container">
        <div className="error-container">
          <FaExclamationTriangle />
          <h3>Error al cargar el dashboard</h3>
          <button onClick={loadDashboardData}>Reintentar</button>
        </div>
      </div>
    );
  }

  const {
    stats,
    recentAlerts,
    studentActivity,
    emotionTrends,
    interventionStats,
    performanceMetrics,
    upcomingTasks,
    quickInsights
  } = dashboardData;

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

  return (
    <div className="dashboard-tutor-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <div className="logo-section">
            <FaGraduationCap className="logo-icon" />
            <h1>Dashboard de Tutor</h1>
          </div>
        </div>

        <div className="header-center">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 90 días</option>
          </select>
        </div>

        <div className="header-right">
          <button
            className="notifications-btn"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <FaBell />
            {stats.unreadNotifications > 0 && (
              <span className="notification-badge">{stats.unreadNotifications}</span>
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
      <div className="dashboard-main">
        {/* Métricas principales */}
        <div className="metrics-grid">
          <div className="metric-card critical">
            <div className="metric-icon">
              <FaExclamationTriangle />
            </div>
            <div className="metric-content">
              <h3>Alertas Críticas</h3>
              <div className="metric-value">{stats.criticalAlerts}</div>
              <div className="metric-trend">
                <FaTrendingUp />
                <span>+{stats.criticalAlertsChange}%</span>
              </div>
            </div>
          </div>

          <div className="metric-card students">
            <div className="metric-icon">
              <FaUsers />
            </div>
            <div className="metric-content">
              <h3>Estudiantes Activos</h3>
              <div className="metric-value">{stats.activeStudents}</div>
              <div className="metric-trend">
                <FaTrendingUp />
                <span>+{stats.activeStudentsChange}%</span>
              </div>
            </div>
          </div>

          <div className="metric-card interventions">
            <div className="metric-icon">
              <FaComments />
            </div>
            <div className="metric-content">
              <h3>Intervenciones</h3>
              <div className="metric-value">{stats.totalInterventions}</div>
              <div className="metric-trend">
                <FaTrendingDown />
                <span>-{stats.interventionsChange}%</span>
              </div>
            </div>
          </div>

          <div className="metric-card performance">
            <div className="metric-icon">
              <FaTachometerAlt />
            </div>
            <div className="metric-content">
              <h3>Rendimiento</h3>
              <div className="metric-value">{stats.performanceScore}%</div>
              <div className="metric-trend">
                <FaTrendingUp />
                <span>+{stats.performanceChange}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Gráficos y análisis */}
        <div className="charts-section">
          <div className="chart-container">
            <h3>Tendencias Emocionales</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={emotionTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="anxiety" stroke="#e53e3e" strokeWidth={2} />
                <Line type="monotone" dataKey="depression" stroke="#3182ce" strokeWidth={2} />
                <Line type="monotone" dataKey="stress" stroke="#d69e2e" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>Distribución de Alertas</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.alertDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {stats.alertDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alertas recientes */}
        <div className="recent-alerts-section">
          <div className="section-header">
            <h3>Alertas Recientes</h3>
            <button onClick={() => navigate('/tutor/panel')} className="view-all-btn">
              Ver todas
            </button>
          </div>
          <div className="alerts-grid">
            {recentAlerts.slice(0, 6).map((alert) => (
              <div key={alert.id} className="alert-card">
                <div className="alert-header">
                  <div className="student-info">
                    <FaUser className="student-avatar" />
                    <div>
                      <h4>{alert.studentName}</h4>
                      <p>{alert.studentEmail}</p>
                    </div>
                  </div>
                  <span className={`urgency-badge ${alert.urgency}`}>
                    {alert.urgency}
                  </span>
                </div>
                <p className="alert-message">{alert.message}</p>
                <div className="alert-footer">
                  <span className="alert-time">
                    <FaClock />
                    {alert.timeAgo}
                  </span>
                  <button onClick={() => navigate(`/tutor/chat/${alert.studentId}`)}>
                    <FaComments />
                    Intervenir
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actividad de estudiantes */}
        <div className="student-activity-section">
          <h3>Actividad de Estudiantes</h3>
          <div className="activity-grid">
            {studentActivity.map((student) => (
              <div key={student.id} className="activity-card">
                <div className="activity-header">
                  <FaUser className="student-avatar" />
                  <div>
                    <h4>{student.name}</h4>
                    <p>{student.email}</p>
                  </div>
                  <span className={`status-badge ${student.status}`}>
                    {student.status}
                  </span>
                </div>
                <div className="activity-metrics">
                  <div className="metric">
                    <span>Mensajes</span>
                    <span>{student.messageCount}</span>
                  </div>
                  <div className="metric">
                    <span>Última actividad</span>
                    <span>{student.lastActivity}</span>
                  </div>
                  <div className="metric">
                    <span>Emoción predominante</span>
                    <span className="emotion-badge">{student.predominantEmotion}</span>
                  </div>
                </div>
                <div className="activity-actions">
                  <button onClick={() => navigate(`/tutor/chat/${student.id}`)}>
                    <FaComments />
                    Chat
                  </button>
                  <button onClick={() => navigate(`/tutor/student/${student.id}/analysis`)}>
                    <FaBrain />
                    Análisis
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights rápidos */}
        <div className="insights-section">
          <h3>Insights Rápidos</h3>
          <div className="insights-grid">
            {quickInsights.map((insight, index) => (
              <div key={index} className="insight-card">
                <div className="insight-icon">
                  <FaLightbulb />
                </div>
                <h4>{insight.title}</h4>
                <p>{insight.description}</p>
                <div className="insight-metrics">
                  <span>Confianza: {insight.confidence}%</span>
                  <span>Impacto: {insight.impact}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tareas próximas */}
        <div className="upcoming-tasks-section">
          <h3>Tareas Próximas</h3>
          <div className="tasks-list">
            {upcomingTasks.map((task) => (
              <div key={task.id} className="task-item">
                <div className="task-info">
                  <FaCalendarAlt className="task-icon" />
                  <div>
                    <h4>{task.title}</h4>
                    <p>{task.description}</p>
                  </div>
                </div>
                <div className="task-meta">
                  <span className="task-priority">{task.priority}</span>
                  <span className="task-deadline">{task.deadline}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Panel de notificaciones */}
      {showNotifications && (
        <NotificacionesTutor onClose={() => setShowNotifications(false)} />
      )}
    </div>
  );
};

export default DashboardTutor; 