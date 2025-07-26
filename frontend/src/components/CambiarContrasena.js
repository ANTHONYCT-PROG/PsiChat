import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { showNotification } from '../utils/notifications';
import logger from '../utils/logger';
import { FaArrowLeft, FaLock, FaSave } from 'react-icons/fa';
import './CambiarContrasena.css';

const CambiarContrasena = () => {
  const navigate = useNavigate();
  const { user, updatePassword } = useAuth(); // Asumiendo que existe una función updatePassword en AuthContext
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    if (newPassword !== confirmNewPassword) {
      setError('Las nuevas contraseñas no coinciden.');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setError('La nueva contraseña debe tener al menos 6 caracteres.');
      setLoading(false);
      return;
    }

    try {
      // Aquí se llamaría a la función para actualizar la contraseña en el backend
      // Por ahora, simulamos una llamada exitosa
      // await updatePassword(oldPassword, newPassword);
      logger.info('Simulando cambio de contraseña', { userId: user?.id });
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simular API call

      setSuccess('Contraseña actualizada exitosamente.');
      setOldPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
      showNotification.success('Contraseña actualizada exitosamente.');
    } catch (err) {
      logger.error('Error al cambiar contraseña', err);
      setError(err.response?.data?.detail || 'Error al actualizar la contraseña.');
      showNotification.error('Error al actualizar la contraseña.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cambiar-contrasena-container">
      <div className="cambiar-contrasena-card">
        <div className="card-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <FaArrowLeft />
          </button>
          <h1><FaLock /> Cambiar Contraseña</h1>
        </div>
        <p className="subtitle">Actualiza tu contraseña para mantener tu cuenta segura.</p>

        <form onSubmit={handleSubmit} className="password-form">
          <div className="form-group">
            <label htmlFor="oldPassword">Contraseña Actual</label>
            <input
              type="password"
              id="oldPassword"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">Nueva Contraseña</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmNewPassword">Confirmar Nueva Contraseña</label>
            <input
              type="password"
              id="confirmNewPassword"
              value={confirmNewPassword}
              onChange={(e) => setConfirmNewPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className="message error">{error}</div>}
          {success && <div className="message success">{success}</div>}

          <button type="submit" className="save-btn" disabled={loading}>
            {loading ? 'Guardando...' : <><FaSave /> Guardar Cambios</>}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CambiarContrasena; 