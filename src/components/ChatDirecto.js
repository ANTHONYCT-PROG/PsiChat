import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { chatService } from '../services/api';
import logger from '../utils/logger';
import { showNotification } from '../utils/notifications';
import { FaArrowLeft, FaPaperPlane, FaUser, FaRobot, FaSpinner } from 'react-icons/fa';
import './ChatDirecto.css';

const ChatDirecto = () => {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
  const initializeChat = async () => {
      setLoading(true);
    try {
        // Cargar información del participante
        const participantInfo = await chatService.getParticipantInfo(studentId);
        setParticipant(participantInfo);
        logger.chat('Información del participante cargada', { participantId: studentId });

        // Cargar historial de mensajes
        const chatHistory = await chatService.getDirectChatHistory(studentId);
        setMessages(chatHistory);
        logger.chat('Historial de chat directo cargado', { 
          participantId: studentId, 
          messageCount: chatHistory.length 
        });
    } catch (error) {
        logger.error('Error al inicializar chat directo', error);
        showNotification.error('Error al cargar el chat');
      } finally {
        setLoading(false);
      }
    };

    if (studentId) {
      initializeChat();
    }
  }, [studentId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;

    const messageData = {
      content: newMessage.trim(),
      sender_id: user.id,
      receiver_id: studentId,
      timestamp: new Date().toISOString(),
    };

    setSending(true);
    try {
      const sentMessage = await chatService.sendDirectMessage(messageData);
      setMessages(prev => [...prev, sentMessage]);
      setNewMessage('');
      logger.chat('Mensaje directo enviado', { 
        receiverId: studentId, 
        messageId: sentMessage.id 
      });
    } catch (error) {
      logger.error('Error al enviar mensaje directo', error);
      showNotification.error('Error al enviar el mensaje');
    } finally {
      setSending(false);
    }
  };

  const handleAnalysis = async () => {
    setLoadingAnalysis(true);
    try {
      const analysis = await chatService.getLastAnalysis(studentId);
      navigate('/analisis', { 
        state: { 
          analysis: analysis.analysis_data, 
          completeAnalysis: analysis 
        } 
      });
      logger.analysis('Navegación a análisis desde chat directo', { studentId });
    } catch (error) {
      logger.error('Error al obtener análisis para navegación', error);
      showNotification.error('Error al cargar el análisis');
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const handleEndChat = () => {
    navigate(-1);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSenderName = (sender) => {
    return sender === user.id ? user.nombre : participant?.nombre || 'Usuario';
  };

  const getSenderAvatar = (sender) => {
    return sender === user.id ? <FaUser /> : <FaRobot />;
  };

  if (loading) {
    return (
      <div className="chat-directo-container">
        <div className="loading-container">
          <FaSpinner className="loading-spinner" />
          <p>Cargando chat...</p>
        </div>
      </div>
    );
    }

  return (
    <div className="chat-directo-container">
      {/* Header */}
      <div className="chat-directo-header">
        <div className="header-content">
          <div className="header-left">
            <button className="back-btn" onClick={handleEndChat}>
              <FaArrowLeft />
            </button>
              <div className="participant-info">
                <div className="participant-avatar">
                <FaUser />
                </div>
                <div className="participant-details">
                <h2>{participant?.nombre || 'Usuario'}</h2>
                <p>{participant?.email || 'Sin información'}</p>
              </div>
            </div>
          </div>
          <div className="header-actions">
            <button 
              className="analysis-btn"
              onClick={handleAnalysis}
              disabled={loadingAnalysis}
            >
              {loadingAnalysis ? <FaSpinner className="spinner-icon" /> : <FaChartLine />}
                Análisis
              </button>
            <button className="end-chat-btn" onClick={handleEndChat}>
              ×
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        <div className="messages-list">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.sender_id === user.id ? 'sent-message' : 'received-message'}`}
            >
              <div className="message-avatar">
                {getSenderAvatar(message.sender_id)}
              </div>
              <div className="message-content">
                <div className="message-header">
                  <span className="sender-name">{getSenderName(message.sender_id)}</span>
                  <span className="message-time">{formatTime(message.timestamp)}</span>
                </div>
                <div className="message-text">{message.content}</div>
                {message.emotion && (
                  <div className="emotion-indicator">
                    <span className="emotion-icon">💭</span>
                    <span className="emotion-label">{message.emotion}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Footer */}
      <div className="chat-directo-footer">
        <div className="chat-controls">
          <form className="message-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              className="message-input"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Escribe tu mensaje..."
              disabled={sending}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={!newMessage.trim() || sending}
            >
              {sending ? <FaSpinner /> : <FaPaperPlane />}
            </button>
          </form>
          </div>
        </div>
    </div>
  );
};

export default ChatDirecto; 