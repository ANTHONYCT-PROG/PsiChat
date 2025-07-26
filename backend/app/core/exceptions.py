"""
Sistema de excepciones personalizadas para el manejo robusto de errores.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class PsiChatException(Exception):
    """Excepción base para todas las excepciones de PsiChat."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(PsiChatException):
    """Error de autenticación."""
    
    def __init__(self, message: str = "Error de autenticación", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(PsiChatException):
    """Error de autorización."""
    
    def __init__(self, message: str = "No tienes permisos para realizar esta acción", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="AUTHZ_ERROR",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ValidationError(PsiChatException):
    """Error de validación de datos."""
    
    def __init__(self, message: str = "Datos inválidos", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class NotFoundError(PsiChatException):
    """Recurso no encontrado."""
    
    def __init__(self, resource: str = "Recurso", details: Dict[str, Any] = None):
        super().__init__(
            message=f"{resource} no encontrado",
            error_code="NOT_FOUND",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DatabaseError(PsiChatException):
    """Error de base de datos."""
    
    def __init__(self, message: str = "Error en la base de datos", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DB_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AnalysisError(PsiChatException):
    """Error en el análisis emocional."""
    
    def __init__(self, message: str = "Error en el análisis emocional", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ChatError(PsiChatException):
    """Error en el chat."""
    
    def __init__(self, message: str = "Error en el chat", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="CHAT_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalServiceError(PsiChatException):
    """Error en servicio externo."""
    
    def __init__(self, service: str, message: str = None, details: Dict[str, Any] = None):
        msg = message or f"Error en el servicio {service}"
        super().__init__(
            message=msg,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            status_code=status.HTTP_502_BAD_GATEWAY
        )


class RateLimitError(PsiChatException):
    """Error de límite de tasa."""
    
    def __init__(self, message: str = "Límite de solicitudes excedido", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ConflictError(PsiChatException):
    """Error de conflicto (por ejemplo, recurso ya existente)."""
    def __init__(self, message: str = "Conflicto de recurso", details: dict = None):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details,
            status_code=status.HTTP_409_CONFLICT
        )


def handle_psichat_exception(exc: PsiChatException) -> HTTPException:
    """Convierte una excepción de PsiChat en HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


def handle_generic_exception(exc: Exception) -> HTTPException:
    """Maneja excepciones genéricas."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "INTERNAL_ERROR",
            "message": "Error interno del servidor",
            "details": {"type": type(exc).__name__}
        }
    ) 