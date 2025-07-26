import axios from 'axios';
import { currentConfig } from '../config/environment';

// Configuración base de axios
const API_BASE_URL = currentConfig.apiBaseUrl;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Servicio de autenticación
export const authService = {
  setToken: (token) => {
    localStorage.setItem('token', token);
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  },

  removeToken: () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { username: email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  getStudents: async () => {
    const response = await api.get('/auth/students');
    return response.data;
  },

  changePassword: async (oldPassword, newPassword) => {
    const response = await api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword });
    return response.data;
  },
};

// Servicio de chat
export const chatService = {
  sendMessage: async (message) => {
    const response = await api.post('/chat/', message);
    return response.data;
  },

  getChatHistory: async () => {
    const response = await api.get('/chat/history');
    return response.data;
  },

  getConversation: async (studentId) => {
    const response = await api.get(`/chat/conversation/${studentId}`);
    return response.data;
  },

  getParticipantInfo: async (participantId) => {
    const response = await api.get(`/users/${participantId}`); // Asumiendo un endpoint de usuarios
    return response.data;
  },

  getDirectChatHistory: async (participantId) => {
    const response = await api.get(`/chat/direct/${participantId}`);
    return response.data;
  },

  sendDirectMessage: async (messageData) => {
    const response = await api.post('/chat/direct', messageData);
    return response.data;
  },

  getLastAnalysis: async (studentId) => {
    const response = await api.get(`/analysis/last/${studentId}`); // Asumiendo un endpoint para el último análisis de un estudiante
    return response.data;
  },
};

// Servicio de análisis
export const analysisService = {
  analyzeMessage: async (message) => {
    const response = await api.post('/analysis/analyze', { message });
    return response.data;
  },

  analyzeComplete: async (message) => {
    const response = await api.post('/analysis/complete', { texto: message });
    return response.data;
  },

  getLastAnalysis: async () => {
    const response = await api.get('/analysis/last');
    return response.data;
  },

  getAnalysisHistory: async () => {
    const response = await api.get('/analysis/history');
    return response.data;
  },

  getDeepAnalysis: async () => {
    const response = await api.get('/analysis/deep');
    return response.data;
  },

  getStudentAnalysis: async (studentId) => {
    const response = await api.get(`/analysis/student/${studentId}`);
    return response.data;
  },

  exportAnalysisReport: async (timeRange) => {
    const response = await api.get(`/analysis/export-report`, { params: { time_range: timeRange } });
    return response.data;
  },
};

// Servicio de notificaciones
export const notificationService = {
  getNotifications: async () => {
    const response = await api.get('/notifications');
    return response.data;
  },

  markAsRead: async (notificationId) => {
    const response = await api.put(`/notifications/${notificationId}/read`);
    return response.data;
  },

  createNotification: async (notificationData) => {
    const response = await api.post('/notifications', notificationData);
    return response.data;
  },

  getTutorNotifications: async () => {
    const response = await api.get('/tutor/notifications');
    return response.data;
  },

  markTutorNotificationAsRead: async (notificationId) => {
    const response = await api.put(`/tutor/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllTutorNotificationsAsRead: async () => {
    const response = await api.put('/tutor/notifications/mark-all-read');
    return response.data;
  },

  deleteTutorNotification: async (notificationId) => {
    const response = await api.delete(`/tutor/notifications/${notificationId}`);
    return response.data;
  },
};

// Servicio de usuario y configuración
export const userService = {
  getSettings: async () => {
    const response = await api.get('/user/settings');
    return response.data;
  },
  updateSettings: async (settingsData) => {
    const response = await api.put('/user/settings', settingsData);
    return response.data;
  },
  resetSettings: async () => {
    const response = await api.post('/user/settings/reset');
    return response.data;
  },
  getProfile: async () => {
    const response = await api.get('/user/profile');
    return response.data;
  },
  updateProfile: async (profileData) => {
    const response = await api.put('/user/profile', profileData);
    return response.data;
  },
  getProfileStats: async () => {
    const response = await api.get('/user/profile/stats');
    return response.data;
  },
  getDashboardData: async (params) => {
    const response = await api.get('/tutor/dashboard', { params });
    return response.data;
  },
  getAlerts: async () => {
    const response = await api.get('/tutor/alerts');
    return response.data;
  },
  getStudentConversation: async (studentId) => {
    const response = await api.get(`/tutor/student/${studentId}/conversation`);
    return response.data;
  },
  sendIntervention: async (studentId, message) => {
    const response = await api.post('/tutor/intervene', {
      student_id: studentId,
      message: message,
    });
    return response.data;
  },
  markAlertAsReviewed: async (alertId, notes = null, actionTaken = null) => {
    const response = await api.put(`/tutor/alert/${alertId}/review`, {
      notes: notes,
      action_taken: actionTaken,
    });
    return response.data;
  },
  getStudents: async () => {
    const response = await api.get('/tutor/students');
    return response.data;
  },
  getStudentAnalysis: async (studentId) => {
    const response = await api.get(`/tutor/student/${studentId}/analysis`);
    return response.data;
  },
  generateReport: async (startDate, endDate, reportType = 'general') => {
    const response = await api.post('/tutor/reports', {
      start_date: startDate,
      end_date: endDate,
      report_type: reportType,
    });
    return response.data;
  },
};

export default api; 