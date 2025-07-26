import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import {
  FaCog,
  FaSave,
  FaSyncAlt,
  FaBell,
  FaExclamationTriangle,
  FaPalette,
  FaLock,
  FaUser,
  FaSignOutAlt,
  FaDownload,
  FaUpload,
  FaTimes,
  FaCheckCircle,
} from 'react-icons/fa';
import './Configuracion.css';

const Configuracion = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      critical_alerts: true,
      high_alerts: true,
      medium_alerts: false,
      low_alerts: false,
      daily_summary: true,
      weekly_report: true
    },
    alerts: {
      auto_intervention: false,
      intervention_threshold: 'high',
      alert_cooldown: 30,
      max_daily_alerts: 50
    },
    display: {
      theme: 'light',
      language: 'es',
      timezone: 'America/Mexico_City',
      date_format: 'DD/MM/YYYY',
      time_format: '24h'
    },
    privacy: {
      share_analytics: true,
      share_anonymized_data: false,
      allow_research: false
    }
  });

  useEffect(() => {
    if (user) {
      loadSettings();
    }
  }, [user]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await userService.getSettings();
      if (response) {
        setSettings(response);
      }
    } catch (err) {
      console.error('Error cargando configuración:', err);
      setError('Error al cargar la configuración');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      await userService.updateSettings(settings);
      setSuccess('Configuración guardada exitosamente');
      
      // Limpiar mensaje de éxito después de 3 segundos
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Error guardando configuración:', err);
      setError('Error al guardar la configuración');
    } finally {
      setSaving(false);
    }
  };

  const resetSettings = async () => {
    if (window.confirm('¿Estás seguro de que quieres restaurar la configuración por defecto?')) {
      try {
        setLoading(true);
        await userService.resetSettings();
        await loadSettings();
        setSuccess('Configuración restaurada exitosamente');
        setTimeout(() => setSuccess(null), 3000);
      } catch (err) {
        console.error('Error restaurando configuración:', err);
        setError('Error al restaurar la configuración');
      } finally {
        setLoading(false);
      }
    }
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `configuracion_${user?.nombre || 'tutor'}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const importSettings = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          setSettings(importedSettings);
          setSuccess('Configuración importada exitosamente');
          setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
          setError('Error al importar la configuración: archivo inválido');
        }
      };
      reader.readAsText(file);
    }
  };

  if (loading) {
    return (
      <div className="configuracion-container">
        <div className="loading-container">
          <div className="spinner">⏳</div>
          <p>Cargando configuración...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="configuracion-container">
      {/* Header */}
      <div className="configuracion-header">
        <div className="header-left">
          <h1><FaCog /> Configuración</h1>
          <p>Personaliza tu experiencia en PsiChat</p>
        </div>
        <div className="header-actions">
          <button 
            className="save-btn"
            onClick={saveSettings}
            disabled={saving}
          >
            {saving ? <><FaSave /> Guardando...</> : <><FaSave /> Guardar Cambios</>}
          </button>
          <button 
            className="reset-btn"
            onClick={resetSettings}
            disabled={loading}
          >
            <FaSyncAlt /> Restaurar
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="message error">
          <span><FaTimes /> {error}</span>
          <button onClick={() => setError(null)}><FaTimes /></button>
        </div>
      )}
      
      {success && (
        <div className="message success">
          <span><FaCheckCircle /> {success}</span>
          <button onClick={() => setSuccess(null)}><FaTimes /></button>
        </div>
      )}

      {/* Settings Sections */}
      <div className="settings-grid">
        {/* Notificaciones */}
        <div className="settings-section">
          <div className="section-header">
            <h2><FaBell /> Notificaciones</h2>
            <p>Configura cómo recibir alertas y notificaciones</p>
          </div>
          
          <div className="settings-group">
            <h3>Tipos de Notificación</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <label>Notificaciones por Email</label>
                <p>Recibe alertas importantes en tu correo electrónico</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.notifications.email}
                  onChange={(e) => updateSetting('notifications', 'email', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Notificaciones Push</label>
                <p>Recibe notificaciones en tiempo real en el navegador</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.notifications.push}
                  onChange={(e) => updateSetting('notifications', 'push', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Alertas Críticas</label>
                <p>Notificaciones inmediatas para situaciones críticas</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.notifications.critical_alerts}
                  onChange={(e) => updateSetting('notifications', 'critical_alerts', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Alertas Altas</label>
                <p>Notificaciones para situaciones de alta prioridad</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.notifications.high_alerts}
                  onChange={(e) => updateSetting('notifications', 'high_alerts', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Resumen Diario</label>
                <p>Recibe un resumen diario de actividad</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.notifications.daily_summary}
                  onChange={(e) => updateSetting('notifications', 'daily_summary', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Reporte Semanal</label>
                <p>Recibe un reporte semanal detallado</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.notifications.weekly_report}
                  onChange={(e) => updateSetting('notifications', 'weekly_report', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </div>

        {/* Alertas */}
        <div className="settings-section">
          <div className="section-header">
            <h2><FaExclamationTriangle /> Alertas</h2>
            <p>Configura el comportamiento del sistema de alertas</p>
          </div>
          
          <div className="settings-group">
            <h3>Configuración de Alertas</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <label>Intervención Automática</label>
                <p>Permite que el sistema sugiera intervenciones automáticamente</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.alerts.auto_intervention}
                  onChange={(e) => updateSetting('alerts', 'auto_intervention', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Umbral de Intervención</label>
                <p>Nivel mínimo de urgencia para sugerir intervención</p>
              </div>
              <select
                value={settings.alerts.intervention_threshold}
                onChange={(e) => updateSetting('alerts', 'intervention_threshold', e.target.value)}
              >
                <option value="critical">Crítica</option>
                <option value="high">Alta</option>
                <option value="medium">Media</option>
                <option value="low">Baja</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Tiempo de Enfriamiento (minutos)</label>
                <p>Tiempo mínimo entre alertas del mismo tipo</p>
              </div>
              <input
                type="number"
                min="1"
                max="120"
                value={settings.alerts.alert_cooldown}
                onChange={(e) => updateSetting('alerts', 'alert_cooldown', parseInt(e.target.value))}
              />
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Máximo de Alertas Diarias</label>
                <p>Límite de alertas por día para evitar spam</p>
              </div>
              <input
                type="number"
                min="1"
                max="200"
                value={settings.alerts.max_daily_alerts}
                onChange={(e) => updateSetting('alerts', 'max_daily_alerts', parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>

        {/* Visualización */}
        <div className="settings-section">
          <div className="section-header">
            <h2><FaPalette /> Visualización</h2>
            <p>Personaliza la apariencia y formato de la interfaz</p>
          </div>
          
          <div className="settings-group">
            <h3>Apariencia</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <label>Tema</label>
                <p>Elige entre tema claro u oscuro</p>
              </div>
              <select
                value={settings.display.theme}
                onChange={(e) => updateSetting('display', 'theme', e.target.value)}
              >
                <option value="light">Claro</option>
                <option value="dark">Oscuro</option>
                <option value="auto">Automático</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Idioma</label>
                <p>Idioma de la interfaz</p>
              </div>
              <select
                value={settings.display.language}
                onChange={(e) => updateSetting('display', 'language', e.target.value)}
              >
                <option value="es">Español</option>
                <option value="en">English</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Zona Horaria</label>
                <p>Zona horaria para mostrar fechas y horas</p>
              </div>
              <select
                value={settings.display.timezone}
                onChange={(e) => updateSetting('display', 'timezone', e.target.value)}
              >
                <option value="America/Mexico_City">Ciudad de México</option>
                <option value="America/New_York">Nueva York</option>
                <option value="America/Los_Angeles">Los Ángeles</option>
                <option value="Europe/Madrid">Madrid</option>
                <option value="UTC">UTC</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Formato de Fecha</label>
                <p>Formato para mostrar fechas</p>
              </div>
              <select
                value={settings.display.date_format}
                onChange={(e) => updateSetting('display', 'date_format', e.target.value)}
              >
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
              </select>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Formato de Hora</label>
                <p>Formato para mostrar horas</p>
              </div>
              <select
                value={settings.display.time_format}
                onChange={(e) => updateSetting('display', 'time_format', e.target.value)}
              >
                <option value="24h">24 horas</option>
                <option value="12h">12 horas</option>
              </select>
            </div>
          </div>
        </div>

        {/* Privacidad */}
        <div className="settings-section">
          <div className="section-header">
            <h2><FaLock /> Privacidad</h2>
            <p>Configura tus preferencias de privacidad y datos</p>
          </div>
          
          <div className="settings-group">
            <h3>Datos y Análisis</h3>
            
            <div className="setting-item">
              <div className="setting-info">
                <label>Compartir Análisis</label>
                <p>Permite compartir análisis anónimos para mejorar el sistema</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.privacy.share_analytics}
                  onChange={(e) => updateSetting('privacy', 'share_analytics', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Datos Anonimizados</label>
                <p>Compartir datos completamente anonimizados para investigación</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.privacy.share_anonymized_data}
                  onChange={(e) => updateSetting('privacy', 'share_anonymized_data', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-item">
              <div className="setting-info">
                <label>Participar en Investigación</label>
                <p>Permitir que tus datos sean utilizados para investigación académica</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.privacy.allow_research}
                  onChange={(e) => updateSetting('privacy', 'allow_research', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Import/Export */}
      <div className="import-export-section">
        <div className="section-header">
          <h2><FaDownload /> Importar/Exportar</h2>
          <p>Respaldar o restaurar tu configuración</p>
        </div>
        
        <div className="import-export-actions">
          <button className="export-btn" onClick={exportSettings}>
            <FaDownload /> Exportar Configuración
          </button>
          
          <label className="import-btn">
            <FaUpload /> Importar Configuración
            <input
              type="file"
              accept=".json"
              onChange={importSettings}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>

      {/* Account Actions */}
      <div className="account-section">
        <div className="section-header">
          <h2><FaUser /> Cuenta</h2>
          <p>Gestiona tu cuenta y sesión</p>
        </div>
        
        <div className="account-actions">
          <button className="profile-btn" onClick={() => navigate('/perfil')}>
            <FaUser /> Ver Perfil
          </button>
          <button className="password-btn" onClick={() => navigate('/cambiar-contrasena')}>
            <FaLock /> Cambiar Contraseña
          </button>
          <button className="logout-btn" onClick={logout}>
            <FaSignOutAlt /> Cerrar Sesión
          </button>
        </div>
      </div>
    </div>
  );
};

export default Configuracion; 