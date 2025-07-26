import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/api';
import {
  FaUser,
  FaEdit,
  FaSave,
  FaTimes,
  FaChartBar,
  FaUsers,
  FaBrain,
  FaMapMarkerAlt,
  FaCalendarAlt,
  FaAward,
  FaLightbulb,
  FaPlus,
  FaTrash,
  FaSpinner,
  FaCheckCircle,
} from 'react-icons/fa';
import './PerfilUsuario.css';

const PerfilUsuario = () => {
  const { user, updateUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [stats, setStats] = useState(null);
  
  const [profile, setProfile] = useState({
    nombre: '',
    apellido: '',
    email: '',
    telefono: '',
    especialidad: '',
    bio: '',
    ubicacion: '',
    experiencia_anos: 0,
    certificaciones: [],
    areas_interes: [],
    horario_disponible: {
      lunes: { inicio: '09:00', fin: '17:00', disponible: true },
      martes: { inicio: '09:00', fin: '17:00', disponible: true },
      miercoles: { inicio: '09:00', fin: '17:00', disponible: true },
      jueves: { inicio: '09:00', fin: '17:00', disponible: true },
      viernes: { inicio: '09:00', fin: '17:00', disponible: true },
      sabado: { inicio: '09:00', fin: '13:00', disponible: false },
      domingo: { inicio: '09:00', fin: '17:00', disponible: false }
    }
  });

  useEffect(() => {
    if (user) {
      loadProfile();
      loadStats();
    }
  }, [user]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await userService.getProfile();
      if (response) {
        setProfile(response);
      }
    } catch (err) {
      console.error('Error cargando perfil:', err);
      setError('Error al cargar el perfil');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await userService.getProfileStats();
      setStats(response);
    } catch (err) {
      console.error('Error cargando estadísticas:', err);
    }
  };

  const saveProfile = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      const response = await userService.updateProfile(profile);
      if (response) {
        updateUser(response);
        setSuccess('Perfil actualizado exitosamente');
        setEditMode(false);
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error guardando perfil:', err);
      setError('Error al guardar el perfil');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleScheduleChange = (day, field, value) => {
    setProfile(prev => ({
      ...prev,
      horario_disponible: {
        ...prev.horario_disponible,
        [day]: {
          ...prev.horario_disponible[day],
          [field]: value
        }
      }
    }));
  };

  const addCertification = () => {
    setProfile(prev => ({
      ...prev,
      certificaciones: [...prev.certificaciones, '']
    }));
  };

  const removeCertification = (index) => {
    setProfile(prev => ({
      ...prev,
      certificaciones: prev.certificaciones.filter((_, i) => i !== index)
    }));
  };

  const updateCertification = (index, value) => {
    setProfile(prev => ({
      ...prev,
      certificaciones: prev.certificaciones.map((cert, i) => 
        i === index ? value : cert
      )
    }));
  };

  const addInterestArea = () => {
    setProfile(prev => ({
      ...prev,
      areas_interes: [...prev.areas_interes, '']
    }));
  };

  const removeInterestArea = (index) => {
    setProfile(prev => ({
      ...prev,
      areas_interes: prev.areas_interes.filter((_, i) => i !== index)
    }));
  };

  const updateInterestArea = (index, value) => {
    setProfile(prev => ({
      ...prev,
      areas_interes: prev.areas_interes.map((area, i) => 
        i === index ? value : area
      )
    }));
  };

  const getCompletionPercentage = () => {
    const fields = [
      profile.nombre, profile.apellido, profile.email, profile.especialidad,
      profile.bio, profile.ubicacion, profile.experiencia_anos,
      profile.certificaciones.length, profile.areas_interes.length
    ];
    const completed = fields.filter(field => 
      field && (typeof field === 'string' ? field.trim() : field > 0)
    ).length;
    return Math.round((completed / fields.length) * 100);
  };

  if (loading) {
    return (
      <div className="perfil-container">
        <div className="loading-container">
          <div className="spinner">⏳</div>
          <p>Cargando perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="perfil-container">
      {/* Header */}
      <div className="perfil-header">
        <div className="header-left">
          <h1><FaUser /> Perfil de Usuario</h1>
          <p>Gestiona tu información personal y profesional</p>
        </div>
        <div className="header-actions">
          {editMode ? (
            <>
              <button 
                className="save-btn"
                onClick={saveProfile}
                disabled={saving}
              >
                {saving ? <><FaSave /> Guardando...</> : <><FaSave /> Guardar Cambios</>}
              </button>
              <button 
                className="cancel-btn"
                onClick={() => {
                  setEditMode(false);
                  loadProfile();
                }}
                disabled={saving}
              >
                <FaTimes /> Cancelar
              </button>
            </>
          ) : (
            <button 
              className="edit-btn"
              onClick={() => setEditMode(true)}
            >
              <FaEdit /> Editar Perfil
            </button>
          )}
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

      <div className="perfil-content">
        {/* Profile Overview */}
        <div className="profile-overview">
          <div className="profile-card">
            <div className="profile-avatar">
              <div className="avatar-placeholder">
                {profile.nombre ? profile.nombre.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="completion-badge">
                {getCompletionPercentage()}%
              </div>
            </div>
            
            <div className="profile-info">
              <h2>{profile.nombre} {profile.apellido}</h2>
              <p className="role">{user?.rol === 'tutor' ? 'Tutor' : 'Estudiante'}</p>
              <p className="email">{profile.email}</p>
              {profile.especialidad && (
                <p className="specialty"><FaBrain /> {profile.especialidad}</p>
              )}
              {profile.experiencia_anos > 0 && (
                <p className="experience"><FaCalendarAlt /> {profile.experiencia_anos} años de experiencia</p>
              )}
            </div>
          </div>

          {/* Stats */}
          {stats && (
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon"><FaUsers /></div>
                <div className="stat-content">
                  <h3>Estudiantes</h3>
                  <div className="stat-value">{stats.total_estudiantes}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon"><FaChartBar /></div>
                <div className="stat-content">
                  <h3>Intervenciones</h3>
                  <div className="stat-value">{stats.total_intervenciones}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon"><FaBrain /></div>
                <div className="stat-content">
                  <h3>Análisis</h3>
                  <div className="stat-value">{stats.total_analisis}</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon"><FaAward /></div>
                <div className="stat-content">
                  <h3>Calificación</h3>
                  <div className="stat-value">{stats.promedio_calificacion || 'N/A'}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Profile Details */}
        <div className="profile-details">
          <div className="details-section">
            <h3><FaUser /> Información Personal</h3>
            
            <div className="form-grid">
              <div className="form-group">
                <label>Nombre *</label>
                <input
                  type="text"
                  value={profile.nombre}
                  onChange={(e) => handleInputChange('nombre', e.target.value)}
                  disabled={!editMode}
                  placeholder="Tu nombre"
                />
              </div>
              
              <div className="form-group">
                <label>Apellido *</label>
                <input
                  type="text"
                  value={profile.apellido}
                  onChange={(e) => handleInputChange('apellido', e.target.value)}
                  disabled={!editMode}
                  placeholder="Tu apellido"
                />
              </div>
              
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  disabled={!editMode}
                  placeholder="tu@email.com"
                />
              </div>
              
              <div className="form-group">
                <label>Teléfono</label>
                <input
                  type="tel"
                  value={profile.telefono}
                  onChange={(e) => handleInputChange('telefono', e.target.value)}
                  disabled={!editMode}
                  placeholder="+52 123 456 7890"
                />
              </div>
              
              <div className="form-group">
                <label>Especialidad</label>
                <input
                  type="text"
                  value={profile.especialidad}
                  onChange={(e) => handleInputChange('especialidad', e.target.value)}
                  disabled={!editMode}
                  placeholder="Psicología, Educación, etc."
                />
              </div>
              
              <div className="form-group">
                <label>Años de Experiencia</label>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={profile.experiencia_anos}
                  onChange={(e) => handleInputChange('experiencia_anos', parseInt(e.target.value) || 0)}
                  disabled={!editMode}
                />
              </div>
              
              <div className="form-group full-width">
                <label>Ubicación</label>
                <input
                  type="text"
                  value={profile.ubicacion}
                  onChange={(e) => handleInputChange('ubicacion', e.target.value)}
                  disabled={!editMode}
                  placeholder="Ciudad, Estado, País"
                />
              </div>
              
              <div className="form-group full-width">
                <label>Biografía</label>
                <textarea
                  value={profile.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  disabled={!editMode}
                  placeholder="Cuéntanos sobre ti, tu experiencia y especialidades..."
                  rows="4"
                />
              </div>
            </div>
          </div>

          {/* Certifications */}
          <div className="details-section">
            <div className="section-header">
              <h3><FaAward /> Certificaciones</h3>
              {editMode && (
                <button className="add-btn" onClick={addCertification}>
                  <FaPlus /> Agregar
                </button>
              )}
            </div>
            
            {profile.certificaciones.length === 0 ? (
              <p className="empty-state">No hay certificaciones registradas</p>
            ) : (
              <div className="certifications-list">
                {profile.certificaciones.map((cert, index) => (
                  <div key={index} className="certification-item">
                    <input
                      type="text"
                      value={cert}
                      onChange={(e) => updateCertification(index, e.target.value)}
                      disabled={!editMode}
                      placeholder="Nombre de la certificación"
                    />
                    {editMode && (
                      <button 
                        className="remove-btn"
                        onClick={() => removeCertification(index)}
                      >
                        <FaTrash />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Interest Areas */}
          <div className="details-section">
            <div className="section-header">
              <h3><FaLightbulb /> Áreas de Interés</h3>
              {editMode && (
                <button className="add-btn" onClick={addInterestArea}>
                  <FaPlus /> Agregar
                </button>
              )}
            </div>
            
            {profile.areas_interes.length === 0 ? (
              <p className="empty-state">No hay áreas de interés registradas</p>
            ) : (
              <div className="interests-list">
                {profile.areas_interes.map((area, index) => (
                  <div key={index} className="interest-item">
                    <input
                      type="text"
                      value={area}
                      onChange={(e) => updateInterestArea(index, e.target.value)}
                      disabled={!editMode}
                      placeholder="Área de interés"
                    />
                    {editMode && (
                      <button 
                        className="remove-btn"
                        onClick={() => removeInterestArea(index)}
                      >
                        <FaTrash />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Schedule */}
          <div className="details-section">
            <h3><FaCalendarAlt /> Horario Disponible</h3>
            
            <div className="schedule-grid">
              {Object.entries(profile.horario_disponible).map(([day, schedule]) => (
                <div key={day} className="schedule-day">
                  <div className="day-header">
                    <label className="day-label">
                      <input
                        type="checkbox"
                        checked={schedule.disponible}
                        onChange={(e) => handleScheduleChange(day, 'disponible', e.target.checked)}
                        disabled={!editMode}
                      />
                      <span className="day-name">
                        {day.charAt(0).toUpperCase() + day.slice(1)}
                      </span>
                    </label>
                  </div>
                  
                  {schedule.disponible && (
                    <div className="time-inputs">
                      <input
                        type="time"
                        value={schedule.inicio}
                        onChange={(e) => handleScheduleChange(day, 'inicio', e.target.value)}
                        disabled={!editMode}
                      />
                      <span>a</span>
                      <input
                        type="time"
                        value={schedule.fin}
                        onChange={(e) => handleScheduleChange(day, 'fin', e.target.value)}
                        disabled={!editMode}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerfilUsuario;

export default PerfilUsuario; 