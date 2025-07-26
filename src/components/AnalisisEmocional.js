import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analysisService } from '../services/api';
import logger from '../utils/logger';
import { 
  FaBrain, 
  FaExclamationTriangle, 
  FaArrowLeft,
  FaLightbulb,
  FaChartBar,
  FaSpinner,
} from 'react-icons/fa';
import './AnalisisEmocional.css';

const AnalisisEmocional = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [completeAnalysis, setCompleteAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadAnalysis = async () => {
      // Si se pasa análisis desde otra página, usarlo
      if (location.state?.analysis && location.state?.completeAnalysis) {
      setAnalysis(location.state.analysis);
        setCompleteAnalysis(location.state.completeAnalysis);
        return;
      }

      // Si no hay análisis pasado, cargar el último
      setLoading(true);
      setError(null);
      
      try {
        const lastAnalysis = await analysisService.getLastAnalysis();
        logger.analysis('Datos del último análisis cargados', {
          emotion: lastAnalysis.emotion,
          style: lastAnalysis.style,
        });
        
        // Crear el objeto analysis básico para compatibilidad
        const basicAnalysis = {
          emotion_distribution: lastAnalysis.emotion_distribution || [],
          style_distribution: lastAnalysis.style_distribution || [],
          meta: {
            detected_emotion: lastAnalysis.emotion,
            emotion_score: lastAnalysis.emotion_score,
            detected_style: lastAnalysis.style,
            style_score: lastAnalysis.style_score,
            priority: lastAnalysis.priority,
            alert: lastAnalysis.alert,
          },
        };
        
        logger.analysis('Objeto analysis procesado', {
          emotionDistribution: basicAnalysis.emotion_distribution.length,
          styleDistribution: basicAnalysis.style_distribution.length,
        });
        
        setAnalysis(basicAnalysis);
        setCompleteAnalysis(lastAnalysis);
      } catch (err) {
        logger.error('Error al cargar el último análisis', err);
        setError(err.response?.data?.detail || 'Error al cargar el análisis');
      } finally {
        setLoading(false);
      }
    };

    loadAnalysis();
  }, [location.state]);

  if (loading) {
    return (
      <div className="analysis-container">
        <div className="analysis-header">
          <button className="back-btn" onClick={() => navigate('/chat')}>
            <FaArrowLeft />
          </button>
          <h1>Análisis Emocional</h1>
        </div>
        <div className="loading-container">
          <FaSpinner className="loading-spinner" />
          <p>Cargando último análisis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-container">
        <div className="analysis-header">
          <button className="back-btn" onClick={() => navigate('/chat')}>
            <FaArrowLeft />
          </button>
          <h1>Análisis Emocional</h1>
        </div>
        <div className="error-container">
          <p>Error: {error}</p>
          <button onClick={() => navigate('/chat')}>Volver al Chat</button>
        </div>
      </div>
    );
  }

  if (!analysis || !completeAnalysis) {
    return (
      <div className="analysis-container">
        <div className="analysis-header">
          <button className="back-btn" onClick={() => navigate('/chat')}>
            <FaArrowLeft />
          </button>
          <h1>Análisis Emocional</h1>
        </div>
        <div className="no-data">
          <p>No hay datos de análisis disponibles.</p>
          <p>Envía un mensaje en el chat para generar tu primer análisis.</p>
          <button onClick={() => navigate('/chat')}>Volver al Chat</button>
        </div>
      </div>
    );
  }

  const { 
    emotion, 
    emotion_score, 
    style, 
    style_score, 
    priority, 
    alert, 
    recommendations, 
    summary, 
    detailed_insights,
    message_text,
    analysis_date,
  } = completeAnalysis;

  const { meta } = analysis;
  // Extraer distribuciones completas
  const emotionDistribution = analysis.emotion_distribution || [];
  const styleDistribution = analysis.style_distribution || [];
  logger.analysis('Distribuciones procesadas', {
    emotions: emotionDistribution.length,
    styles: styleDistribution.length,
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'alta': return '#e53e3e';
      case 'media': return '#d69e2e';
      default: return '#38a169';
    }
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      'alegría': '#38a169',
      'tristeza': '#3182ce',
      'ansiedad': '#d69e2e',
      'frustración': '#e53e3e',
      'calma': '#38b2ac',
      'desánimo': '#805ad5',
    };
    return colors[emotion] || '#718096';
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="analysis-container">
      {/* Header */}
      <div className="analysis-header">
        <button className="back-btn" onClick={() => navigate('/chat')}>
          <FaArrowLeft />
        </button>
        <div className="header-content">
          <h1>Análisis Emocional Completo</h1>
          <p>Análisis detallado del último mensaje</p>
          {analysis_date && (
            <p className="analysis-date">Realizado el: {formatDate(analysis_date)}</p>
          )}
        </div>
      </div>

      {/* Mensaje analizado */}
      {message_text && (
        <div className="message-preview">
          <h3>📝 Mensaje Analizado</h3>
          <div className="message-content">
            <p>&ldquo;{message_text}&rdquo;</p>
          </div>
        </div>
      )}

      {/* Tabs de navegación */}
      <div className="analysis-tabs">
        <button 
          className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          <FaChartBar />
          Resumen
        </button>
        <button 
          className={`tab-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          <FaLightbulb />
          Recomendaciones
        </button>
        <button 
          className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          <FaBrain />
          Insights Detallados
        </button>
      </div>

      {/* Contenido de las tabs */}
      <div className="analysis-content">
        {activeTab === 'summary' && (
          <div className="summary-tab">
            {/* Resumen ejecutivo */}
            <div className="summary-card executive">
              <h3>📋 Resumen Ejecutivo</h3>
              <p>{summary.executive}</p>
            </div>

            {/* Estado emocional */}
            <div className="summary-card emotion">
              <h3>💙 Estado Emocional</h3>
              <div className="emotion-display">
                <div 
                  className="emotion-badge"
                  style={{ backgroundColor: getEmotionColor(emotion) }}
                >
                  {emotion}
                </div>
                <div className="emotion-score">
                  <div className="score-bar">
                    <div 
                      className="score-fill"
                      style={{ 
                        width: `${emotion_score}%`,
                        backgroundColor: getEmotionColor(emotion),
                      }}
                    ></div>
                  </div>
                  <span>{emotion_score.toFixed(1)}%</span>
                </div>
              </div>
              {/* Distribución completa de emociones */}
              <div className="distribution-list">
                {emotionDistribution.map(([emo, score], idx) => (
                    <div className="distribution-bar" key={emo}>
                      <span className="distribution-label">{emo}</span>
                      <div className="distribution-bar-bg">
                      <div className="distribution-bar-fill" style={{ width: `${score}%`, backgroundColor: getEmotionColor(emo) }}></div>
                      </div>
                      <span className="distribution-score">{score.toFixed(1)}%</span>
                    </div>
                ))}
              </div>
            </div>

            {/* Estilo de comunicación */}
            <div className="summary-card style">
              <h3>💬 Estilo de Comunicación</h3>
              <div className="style-display">
                <div className="style-badge">{style}</div>
                <div className="style-score">
                  <div className="score-bar">
                    <div 
                      className="score-fill"
                      style={{ 
                        width: `${style_score}%`,
                        backgroundColor: '#4299e1',
                      }}
                    ></div>
                  </div>
                  <span>{style_score.toFixed(1)}%</span>
                </div>
              </div>
              {/* Distribución completa de estilos */}
              <div className="distribution-list">
                {styleDistribution.map(([sty, score], idx) => (
                    <div className="distribution-bar" key={sty}>
                      <span className="distribution-label">{sty}</span>
                      <div className="distribution-bar-bg">
                      <div className="distribution-bar-fill" style={{ width: `${score}%`, backgroundColor: '#4299e1' }}></div>
                      </div>
                      <span className="distribution-score">{score.toFixed(1)}%</span>
                    </div>
                ))}
              </div>
            </div>

            {/* Prioridad y alertas */}
            <div className="summary-card priority">
              <h3>⚠️ Evaluación de Prioridad</h3>
              <div className="priority-display">
                <div 
                  className="priority-badge"
                  style={{ backgroundColor: getPriorityColor(priority) }}
                >
                  {priority.toUpperCase()}
                </div>
                {alert && (
                  <div className="alert-badge">
                    <FaExclamationTriangle />
                    Alerta Activa
                  </div>
                )}
              </div>
            </div>

            {/* Resumen amigable */}
            <div className="summary-card user-friendly">
              <h3>💭 Resumen para ti</h3>
              <p>{summary.user_friendly}</p>
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="recommendations-tab">
            <h3>💡 Recomendaciones Personalizadas</h3>
            
            {/* Acciones inmediatas */}
            {recommendations.immediate_actions.length > 0 && (
              <div className="recommendation-section">
                <h4>🚨 Acciones Inmediatas</h4>
                <ul>
                  {recommendations.immediate_actions.map((action, index) => (
                    <li key={index}>{action}</li>
                  ))}
                </ul>
                </div>
            )}

            {/* Apoyo emocional */}
            {recommendations.emotional_support.length > 0 && (
              <div className="recommendation-section">
                <h4>💙 Apoyo Emocional</h4>
                <ul>
                  {recommendations.emotional_support.map((support, index) => (
                    <li key={index}>{support}</li>
                  ))}
                </ul>
            </div>
            )}

            {/* Tips de comunicación */}
            {recommendations.communication_tips.length > 0 && (
              <div className="recommendation-section">
                <h4>💬 Tips de Comunicación</h4>
                <ul>
                  {recommendations.communication_tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
          </div>
            )}

            {/* Sugerencias a largo plazo */}
            {recommendations.long_term_suggestions.length > 0 && (
              <div className="recommendation-section">
                <h4>🎯 Sugerencias a Largo Plazo</h4>
                <ul>
                  {recommendations.long_term_suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                ))}
              </ul>
              </div>
            )}
            </div>
          )}

        {activeTab === 'insights' && (
          <div className="insights-tab">
            <h3>🧠 Insights Detallados</h3>
            
            <div className="insights-grid">
              <div className="insight-card">
                <h4>Estado Emocional</h4>
                <p>{detailed_insights.emotional_state}</p>
              </div>
              
              <div className="insight-card">
                <h4>Estilo de Comunicación</h4>
                <p>{detailed_insights.communication_style}</p>
              </div>
              
              <div className="insight-card">
                <h4>Evaluación de Riesgo</h4>
                <p>{detailed_insights.risk_assessment}</p>
              </div>
              
              <div className="insight-card">
                <h4>Estado de Alerta</h4>
                <p>{detailed_insights.alert_status}</p>
              </div>
            </div>

            {/* Resumen técnico */}
            <div className="technical-summary">
              <h4>📊 Resumen Técnico</h4>
              <p>{summary.technical}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalisisEmocional; 