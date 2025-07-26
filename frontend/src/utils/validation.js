/**
 * Utilidades de validación para PsiChat
 */

import { VALIDATION } from '../constants';

// Validación de email
export const validateEmail = (email) => {
  if (!email) {
    return { isValid: false, message: 'El email es requerido' };
  }
  
  if (!VALIDATION.EMAIL_REGEX.test(email)) {
    return { isValid: false, message: 'El formato del email no es válido' };
  }
  
  return { isValid: true, message: '' };
};

// Validación de contraseña
export const validatePassword = (password) => {
  if (!password) {
    return { isValid: false, message: 'La contraseña es requerida' };
  }
  
  if (password.length < VALIDATION.PASSWORD_MIN_LENGTH) {
    return { 
      isValid: false, 
      message: `La contraseña debe tener al menos ${VALIDATION.PASSWORD_MIN_LENGTH} caracteres` 
    };
  }
  
  // Validar que contenga al menos una letra y un número
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  
  if (!hasLetter || !hasNumber) {
    return { 
      isValid: false, 
      message: 'La contraseña debe contener al menos una letra y un número' 
    };
  }
  
  return { isValid: true, message: '' };
};

// Validación de confirmación de contraseña
export const validatePasswordConfirmation = (password, confirmation) => {
  if (!confirmation) {
    return { isValid: false, message: 'Confirma tu contraseña' };
  }
  
  if (password !== confirmation) {
    return { isValid: false, message: 'Las contraseñas no coinciden' };
  }
  
  return { isValid: true, message: '' };
};

// Validación de nombre
export const validateName = (name) => {
  if (!name) {
    return { isValid: false, message: 'El nombre es requerido' };
  }
  
  if (name.length < VALIDATION.NAME_MIN_LENGTH) {
    return { 
      isValid: false, 
      message: `El nombre debe tener al menos ${VALIDATION.NAME_MIN_LENGTH} caracteres` 
    };
  }
  
  // Validar que solo contenga letras y espacios
  const nameRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
  if (!nameRegex.test(name)) {
    return { isValid: false, message: 'El nombre solo puede contener letras y espacios' };
  }
  
  return { isValid: true, message: '' };
};

// Validación de mensaje
export const validateMessage = (message) => {
  if (!message) {
    return { isValid: false, message: 'El mensaje es requerido' };
  }
  
  if (message.length > VALIDATION.MESSAGE_MAX_LENGTH) {
    return { 
      isValid: false, 
      message: `El mensaje no puede exceder ${VALIDATION.MESSAGE_MAX_LENGTH} caracteres` 
    };
  }
  
  return { isValid: true, message: '' };
};

// Validación de formulario de login
export const validateLoginForm = (formData) => {
  const errors = {};
  
  const emailValidation = validateEmail(formData.email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.message;
  }
  
  const passwordValidation = validatePassword(formData.password);
  if (!passwordValidation.isValid) {
    errors.password = passwordValidation.message;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Validación de formulario de registro
export const validateRegisterForm = (formData) => {
  const errors = {};
  
  const nameValidation = validateName(formData.nombre);
  if (!nameValidation.isValid) {
    errors.nombre = nameValidation.message;
  }
  
  const emailValidation = validateEmail(formData.email);
  if (!emailValidation.isValid) {
    errors.email = emailValidation.message;
  }
  
  const passwordValidation = validatePassword(formData.password);
  if (!passwordValidation.isValid) {
    errors.password = passwordValidation.message;
  }
  
  const confirmationValidation = validatePasswordConfirmation(formData.password, formData.confirmPassword);
  if (!confirmationValidation.isValid) {
    errors.confirmPassword = confirmationValidation.message;
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Validación de configuración
export const validateSettings = (settings) => {
  const errors = {};
  
  // Validar volumen
  if (settings.sound?.volume !== undefined) {
    const volume = parseInt(settings.sound.volume);
    if (isNaN(volume) || volume < 0 || volume > 100) {
      errors.volume = 'El volumen debe estar entre 0 y 100';
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Validación de análisis
export const validateAnalysisData = (data) => {
  const errors = {};
  
  if (!data.emotion) {
    errors.emotion = 'La emoción es requerida';
  }
  
  if (!data.style) {
    errors.style = 'El estilo es requerido';
  }
  
  if (data.emotion_score !== undefined) {
    const score = parseFloat(data.emotion_score);
    if (isNaN(score) || score < 0 || score > 100) {
      errors.emotion_score = 'El puntaje de emoción debe estar entre 0 y 100';
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Sanitización de entrada
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') {
    return input;
  }
  
  // Remover caracteres peligrosos
  return input
    .replace(/[<>]/g, '') // Remover < y >
    .replace(/javascript:/gi, '') // Remover javascript:
    .trim();
};

// Validación de URL
export const validateURL = (url) => {
  try {
    new URL(url);
    return { isValid: true, message: '' };
  } catch {
    return { isValid: false, message: 'La URL no es válida' };
  }
};

// Validación de fecha
export const validateDate = (date) => {
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) {
    return { isValid: false, message: 'La fecha no es válida' };
  }
  
  return { isValid: true, message: '' };
};

// Validación de número
export const validateNumber = (number, min = null, max = null) => {
  const num = parseFloat(number);
  
  if (isNaN(num)) {
    return { isValid: false, message: 'Debe ser un número válido' };
  }
  
  if (min !== null && num < min) {
    return { isValid: false, message: `El valor mínimo es ${min}` };
  }
  
  if (max !== null && num > max) {
    return { isValid: false, message: `El valor máximo es ${max}` };
  }
  
  return { isValid: true, message: '' };
};

// Validación de longitud
export const validateLength = (value, min, max) => {
  if (!value) {
    return { isValid: false, message: 'El campo es requerido' };
  }
  
  const length = value.length;
  
  if (min && length < min) {
    return { isValid: false, message: `Mínimo ${min} caracteres` };
  }
  
  if (max && length > max) {
    return { isValid: false, message: `Máximo ${max} caracteres` };
  }
  
  return { isValid: true, message: '' };
};

export default {
  validateEmail,
  validatePassword,
  validatePasswordConfirmation,
  validateName,
  validateMessage,
  validateLoginForm,
  validateRegisterForm,
  validateSettings,
  validateAnalysisData,
  sanitizeInput,
  validateURL,
  validateDate,
  validateNumber,
  validateLength
}; 