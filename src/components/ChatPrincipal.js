import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { chatService, analysisService } from '../services/api';
import { 
  FaBrain, 
  FaPaperPlane, 
  FaCog, 
  FaUser, 
  FaArrowLeft,
  FaRobot,
  FaChartLine
} from 'react-icons/fa';
import './ChatPrincipal.css';

const ChatPrincipal = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [isAnalyzingDeep, setIsAnalyzingDeep] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Cargar historial de chat
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await chatService.getChatHistory();
      if (!history || history.length === 0) {
        setMessages([
          {
            id: 1,
            content: '¡Bienvenido! Aún no tienes mensajes en tu historial. Escribe tu primer mensaje para comenzar.',
            sender: 'bot',
            timestamp: new Date().toISOString()
          }
        ]);
      } else {
        setMessages(history);
      }
    } catch (error) {
      console.error('Error cargando historial:', error);
      // Si hay un error al cargar el historial, aún mostramos el mensaje de bienvenida
      setMessages([
        {
          id: 1,
          content: '¡Bienvenido! Aún no tienes mensajes en tu historial. Escribe tu primer mensaje para comenzar.',
          sender: 'bot',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || isLoading) return;
    setErrorMessage(null); // Limpiar error al enviar

    const userMessage = {
      id: Date.now(),
      content: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsLoading(true);
    setIsBotTyping(true);

    try {
      // Construir historial en el formato que espera el backend
      const history = messages
        .filter(msg => msg.sender === 'user' || msg.sender === 'bot')
        .map(msg => [msg.sender === 'user' ? msg.content : '', msg.sender === 'bot' ? msg.content : ''])
        .filter(pair => pair[0] || pair[1]);

      // Enviar mensaje al backend con el formato correcto
      const response = await chatService.sendMessage({
        user_text: newMessage,
        history: history
      });
      
      // Guardar emoción y estilo detectados en el mensaje del usuario
      const userMessageWithMeta = {
        ...userMessage,
        emotion: response.meta?.detected_emotion,
        emotion_score: response.meta?.emotion_score,
        style: response.meta?.detected_style,
        style_score: response.meta?.style_score
      };

      // Reemplazar el último mensaje del usuario con la versión que tiene meta
      setMessages(prev => {
        const prevWithoutLast = prev.slice(0, -1);
        return [...prevWithoutLast, userMessageWithMeta];
      });

      const botMessage = {
        id: Date.now() + 1,
        content: response.reply || 'Gracias por tu mensaje. ¿Hay algo más en lo que pueda ayudarte?',
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
      setIsBotTyping(false);
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      setErrorMessage('Lo siento, hubo un error al procesar tu mensaje. ¿Podrías intentarlo de nuevo?');
      const errorMessageObj = {
        id: Date.now() + 1,
        content: error.message || 'Lo siento, hubo un error al procesar tu mensaje. ¿Podrías intentarlo de nuevo?',
        sender: 'bot',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessageObj]);
      setIsBotTyping(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalysis = () => {
    // Navegar directamente a la página de análisis
    navigate('/analisis');
  };

  const handleDeepAnalysis = async () => {
    setIsAnalyzingDeep(true);
    try {
      // Realizar análisis profundo de los últimos 10 mensajes
      const deepAnalysis = await analysisService.getDeepAnalysis({ timeRange: '7d' });
      // Navegar a la página de análisis profundo con los resultados
      navigate('/analisis-profundo', {
        state: {
          deepAnalysis: deepAnalysis
        }
      });
    } catch (error) {
      console.error('Error en análisis profundo:', error);
      setErrorMessage('Error al realizar el análisis profundo. Inténtalo de nuevo.');
    } finally {
      setIsAnalyzingDeep(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <header className="chat-header">
        <div className="header-content improved-header-layout">
          {/* Zona izquierda: botón back */}
          <div className="header-zone header-left">
            <button 
              className="back-btn"
              onClick={() => navigate('/')}
            >
              <FaArrowLeft />
            </button>
          </div>
          {/* Zona centro: título */}
          <div className="header-zone header-center">
            <div className="chat-info">
              <h2>Chat PsiChat</h2>
              <p>Asistente emocional</p>
            </div>
          </div>
          {/* Zona derecha: iconos */}
          <div className="header-zone header-actions">
            <button 
              className="icon-btn"
              onClick={() => navigate('/ayuda')}
              title="Ayuda"
            >
              <FaBrain />
            </button>
            <button 
              className="icon-btn"
              onClick={() => navigate('/configuracion')}
              title="Configuración"
            >
              <FaCog />
            </button>
            <button 
              className="icon-btn"
              onClick={() => navigate('/perfil')}
              title="Perfil"
            >
              <FaUser />
            </button>
          </div>
        </div>
      </header>

      {/* Área de mensajes */}
      <div className="chat-messages">
        {messages.map((msg, idx) => (
            <div 
            key={msg.id}
            className={`message-row ${msg.sender === 'bot' ? 'bot' : 'user'}`}
          >
            {msg.sender === 'bot' && (
              <div className="message-avatar"><FaRobot /></div>
            )}
            <div className={`message-bubble ${msg.sender}`}>
              {msg.content}
              <div className="message-meta">{formatTime(msg.timestamp)}</div>
              {/* Mostrar análisis solo para mensajes del usuario */}
              {msg.sender === 'user' && (msg.emotion || msg.style) && (
                <div className="message-analysis">
                  <span className="emotion-label">Emoción: <b>{msg.emotion || 'N/A'}</b> <span className="emotion-score">({msg.emotion_score ?? ''})</span></span>
                  <span className="style-label">Estilo: <b>{msg.style || 'N/A'}</b> <span className="style-score">({msg.style_score ?? ''})</span></span>
                </div>
              )}
                  </div>
            {msg.sender === 'user' && (
              <div className="message-avatar"><FaUser /></div>
                )}
            </div>
          ))}
        {isBotTyping && (
                <div className="typing-indicator">
            <span>PsiChat está escribiendo</span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            </div>
          )}
        {isLoading && (
          <div className="loading-spinner"></div>
        )}
          <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-section" onSubmit={handleSendMessage}>
          <button 
          type="button" 
          className="btn-analisis" 
            onClick={handleAnalysis}
          title="Ver análisis emocional"
          >
            <FaBrain />
            Ver Análisis
          </button>
          <button 
          type="button" 
          className="btn-analisis-profundo" 
            onClick={handleDeepAnalysis}
          disabled={isAnalyzingDeep}
          title="Ver análisis completo de últimos 10 mensajes"
          >
            <FaChartLine />
            {isAnalyzingDeep ? 'Analizando...' : 'Análisis Completo'}
          </button>
            <input
          className="chat-input"
              type="text"
          placeholder="Escribe tu mensaje..."
              value={newMessage}
          onChange={e => setNewMessage(e.target.value)}
              disabled={isLoading}
            />
        <button className="send-btn" type="submit" disabled={isLoading || !newMessage.trim()}>
              <FaPaperPlane />
            </button>
          </form>
      {errorMessage && (
        <div className="error-message-chat">
          <p>{errorMessage}</p>
          <button onClick={() => setErrorMessage(null)} className="btn btn-secondary">Cerrar</button>
        </div>
      )}
    </div>
  );
};

export default ChatPrincipal; 