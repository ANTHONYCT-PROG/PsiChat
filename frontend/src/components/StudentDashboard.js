import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FaBrain, FaUserTie, FaChartLine, FaUser, FaCog, FaSignOutAlt } from 'react-icons/fa';
import './StudentDashboard.css';

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleAnalysis = () => {
    navigate('/analisis-profundo');
  };

  return (
    <div className="studentchat-bg">
      {/* Header */}
      <header className="studentchat-header">
        <div className="studentchat-header-content">
          <div className="studentchat-welcome">
            <h1>¡Hola, {user?.nombre || 'Estudiante'}!</h1>
            <p>¿En qué puedo ayudarte hoy?</p>
          </div>
          <div className="studentchat-header-actions">
            <button 
              className="icon-btn"
              onClick={() => handleNavigation('/perfil')}
              title="Perfil"
            >
              <FaUser />
            </button>
            <button 
              className="icon-btn"
              onClick={() => handleNavigation('/configuracion')}
              title="Configuración"
            >
              <FaCog />
            </button>
            <button 
              className="icon-btn logout-btn"
              onClick={handleLogout}
              title="Cerrar sesión"
            >
              <FaSignOutAlt />
            </button>
          </div>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="studentchat-main">
        <div className="studentchat-container">
          <div className="studentchat-options-grid">
            {/* Opción 1: Chat con EmotiTutor */}
            <div className="studentchat-option-card primary-card">
              <div className="studentchat-card-icon">
                <FaBrain />
              </div>
              <div className="studentchat-card-content">
                <h3>Habla con PsiChat</h3>
                <p>Conversa con nuestro chatbot emocional y obtén apoyo personalizado</p>
                <button 
                  className="studentchat-btn studentchat-btn-primary"
                  onClick={() => handleNavigation('/chat')}
                >
                  Iniciar chat
                </button>
              </div>
            </div>

            {/* Opción 2: Hablar con Tutor */}
            <div className="studentchat-option-card secondary-card">
              <div className="studentchat-card-icon">
                <FaUserTie />
              </div>
              <div className="studentchat-card-content">
                <h3>Contactar a mi Tutor</h3>
                <p>Comunícate directamente con tu tutor asignado</p>
                <button 
                  className="studentchat-btn studentchat-btn-secondary"
                  onClick={() => handleNavigation(`/chat-directo`)}
                >
                  Hablar con mi tutor
                </button>
              </div>
            </div>
          </div>

          {/* Sección de análisis rápido */}
          <div className="studentchat-quick-analysis">
            <h2>Análisis Rápido</h2>
            <p>Revisa tu estado emocional y progreso</p>
            <button 
              className="studentchat-btn studentchat-btn-success"
              onClick={handleAnalysis}
            >
              <FaChartLine />
              Ver análisis completo
            </button>
          </div>
        </div>
      </main>

      {/* Navegación inferior */}
      <nav className="studentchat-bottom-nav">
        <div className="studentchat-nav-container">
          <button 
            className="studentchat-nav-item active"
            onClick={() => handleNavigation('/')}
          >
            <FaBrain />
            <span>Inicio</span>
          </button>
          <button 
            className="studentchat-nav-item"
            onClick={() => handleNavigation('/chat')}
          >
            <FaBrain />
            <span>Chat</span>
          </button>
          <button 
            className="studentchat-nav-item"
            onClick={() => handleNavigation('/chat-directo')}
          >
            <FaUserTie />
            <span>Tutor</span>
          </button>
          <button 
            className="studentchat-nav-item"
            onClick={() => handleNavigation('/analisis')}
          >
            <FaChartLine />
            <span>Análisis</span>
          </button>
          <button 
            className="studentchat-nav-item"
            onClick={() => handleNavigation('/perfil')}
          >
            <FaUser />
            <span>Perfil</span>
          </button>
        </div>
      </nav>
    </div>
  );
};

export default StudentDashboard; 