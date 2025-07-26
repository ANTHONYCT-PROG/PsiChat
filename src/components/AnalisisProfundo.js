import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analysisService } from '../services/api';
import logger from '../utils/logger';
import { showNotification } from '../utils/notifications';
import {
  FaBrain,
  FaArrowLeft,
  FaChartLine,
  FaSpinner,
  FaTrendingUp,
  FaExclamationTriangle,
  FaLightbulb,
  FaUsers,
  FaEye,
  FaDownload,
  FaShare,
} from 'react-icons/fa';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import './AnalisisProfundo.css';

const AnalisisProfundo = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [deepAnalysis, setDeepAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetrics, setSelectedMetrics] = useState(['emotion', 'style', 'priority']);

  useEffect(() => {
    loadDeepAnalysis();
  }, [timeRange]);

  const loadDeepAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const analysis = await analysisService.getDeepAnalysis({ timeRange });
      setDeepAnalysis(analysis);
      logger.analysis('Análisis profundo cargado', { timeRange, dataPoints: analysis?.data_points?.length });
    } catch (err) {
      logger.error('Error al cargar análisis profundo', err);
      setError(err.response?.data?.detail || 'Error al cargar el análisis profundo');
      showNotification.error('Error al cargar el análisis profundo');
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async () => {
    try {
      const report = await analysisService.exportAnalysisReport(timeRange);
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analisis-profundo-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showNotification.success('Reporte exportado correctamente');
    } catch (error) {
      logger.error('Error al exportar reporte', error);
      showNotification.error('Error al exportar el reporte');
    }
  };

  const handleShareAnalysis = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Mi Análisis Emocional Profundo',
        text: 'Revisa mi análisis emocional completo en PsiChat',
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      showNotification.success('Enlace copiado al portapapeles');
    }
  };

  if (loading) {
    return (
      <div className="analisis-profundo-container">
        <div className="loading-container">
          <FaSpinner className="loading-spinner" />
          <p>Analizando datos profundos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analisis-profundo-container">
        <div className="error-container">
          <FaExclamationTriangle />
          <h3>Error en el análisis</h3>
          <p>{error}</p>
          <button onClick={loadDeepAnalysis}>Reintentar</button>
        </div>
      </div>
    );
  }

  if (!deepAnalysis) {
    return (
      <div className="analisis-profundo-container">
        <div className="no-data">
          <FaBrain />
          <h3>No hay datos para análisis profundo</h3>
          <p>Necesitas más interacciones para generar un análisis profundo</p>
          <button onClick={() => navigate('/chat')}>Ir al Chat</button>
        </div>
      </div>
    );
  }

  const {
    overview,
    trends,
    patterns,
    recommendations,
    insights,
    data_points,
    emotion_distribution,
    style_distribution,
    priority_analysis,
    alert_history,
    improvement_metrics
  } = deepAnalysis;

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

  return (
    <div className="analisis-profundo-container">
      {/* Header */}
      <div className="analisis-profundo-header">
        <button className="back-btn" onClick={() => navigate('/analisis')}>
          <FaArrowLeft />
        </button>
        <div className="header-content">
          <h1>Análisis Emocional Profundo</h1>
          <p>Análisis completo de tu evolución emocional</p>
        </div>
        <div className="header-actions">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 90 días</option>
            <option value="1y">Último año</option>
          </select>
          <button onClick={handleExportReport} className="action-btn">
            <FaDownload />
            Exportar
          </button>
          <button onClick={handleShareAnalysis} className="action-btn">
            <FaShare />
            Compartir
          </button>
        </div>
      </div>

      {/* Tabs de navegación */}
      <div className="analisis-profundo-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FaEye />
          Resumen General
        </button>
        <button
          className={`tab-btn ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          <FaTrendingUp />
          Tendencias
        </button>
        <button
          className={`tab-btn ${activeTab === 'patterns' ? 'active' : ''}`}
          onClick={() => setActiveTab('patterns')}
        >
          <FaBrain />
          Patrones
        </button>
        <button
          className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          <FaLightbulb />
          Insights
        </button>
      </div>

      {/* Contenido de las tabs */}
      <div className="analisis-profundo-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Tarjetas de resumen */}
            <div className="overview-cards">
              <div className="overview-card">
                <div className="card-header">
                  <FaTrendingUp className="card-icon" />
                  <h3>Evolución General</h3>
                </div>
                <div className="card-content">
                  <div className="metric">
                    <span className="metric-label">Tendencia emocional</span>
                    <span className={`metric-value ${overview.emotional_trend === 'positive' ? 'positive' : 'negative'}`}>
                      {overview.emotional_trend === 'positive' ? '↗ Mejorando' : '↘ Necesita atención'}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Estabilidad</span>
                    <span className="metric-value">{overview.stability_score}%</span>
                  </div>
                </div>
              </div>

              <div className="overview-card">
                <div className="card-header">
                  <FaUsers className="card-icon" />
                  <h3>Interacciones</h3>
                </div>
                <div className="card-content">
                  <div className="metric">
                    <span className="metric-label">Total mensajes</span>
                    <span className="metric-value">{overview.total_messages}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Frecuencia</span>
                    <span className="metric-value">{overview.avg_messages_per_day}/día</span>
                  </div>
                </div>
              </div>

              <div className="overview-card">
                <div className="card-header">
                  <FaExclamationTriangle className="card-icon" />
                  <h3>Alertas</h3>
                </div>
                <div className="card-content">
                  <div className="metric">
                    <span className="metric-label">Alertas totales</span>
                    <span className="metric-value">{overview.total_alerts}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Última alerta</span>
                    <span className="metric-value">{overview.days_since_last_alert} días</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Gráfico de evolución temporal */}
            <div className="chart-section">
              <h3>Evolución Temporal</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data_points}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="emotion_score" stroke="#667eea" strokeWidth={2} />
                  <Line type="monotone" dataKey="style_score" stroke="#764ba2" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="trends-tab">
            <div className="trends-grid">
              {trends.map((trend, index) => (
                <div key={index} className="trend-card">
                  <div className="trend-header">
                    <h4>{trend.title}</h4>
                    <span className={`trend-direction ${trend.direction}`}>
                      {trend.direction === 'up' ? '↗' : '↘'}
                    </span>
                  </div>
                  <p>{trend.description}</p>
                  <div className="trend-metrics">
                    <span>Frecuencia: {trend.frequency}</span>
                    <span>Confianza: {trend.confidence}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'patterns' && (
          <div className="patterns-tab">
            <div className="patterns-section">
              <h3>Distribución de Emociones</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={emotion_distribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {emotion_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="patterns-section">
              <h3>Distribución de Estilos</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={style_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="insights-tab">
            <div className="insights-grid">
              {insights.map((insight, index) => (
                <div key={index} className="insight-card">
                  <div className="insight-header">
                    <FaLightbulb className="insight-icon" />
                    <h4>{insight.title}</h4>
                  </div>
                  <p>{insight.description}</p>
                  <div className="insight-metrics">
                    <span>Confianza: {insight.confidence}%</span>
                    <span>Impacto: {insight.impact}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="recommendations-section">
              <h3>Recomendaciones Personalizadas</h3>
              <div className="recommendations-list">
                {recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <div className="recommendation-header">
                      <span className="recommendation-category">{rec.category}</span>
                      <span className="recommendation-priority">{rec.priority}</span>
                    </div>
                    <p>{rec.description}</p>
                    <div className="recommendation-actions">
                      {rec.actions.map((action, actionIndex) => (
                        <button key={actionIndex} className="action-btn small">
                          {action}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalisisProfundo; 