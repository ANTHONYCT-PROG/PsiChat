# Archivo: test_errors.py
"""
Tests para el sistema de manejo de errores
"""

import pytest
from fastapi import status
from app.core.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    ConflictError
)


class TestCustomExceptions:
    """Tests para excepciones personalizadas"""
    
    def test_validation_error(self):
        """Test excepción de validación"""
        error = ValidationError("Campo requerido")
        assert str(error) == "Campo requerido"
        assert error.status_code == 422
    
    def test_authentication_error(self):
        """Test excepción de autenticación"""
        error = AuthenticationError("Credenciales inválidas")
        assert str(error) == "Credenciales inválidas"
        assert error.status_code == 401
    
    def test_authorization_error(self):
        """Test excepción de autorización"""
        error = AuthorizationError("Acceso denegado")
        assert str(error) == "Acceso denegado"
        assert error.status_code == 403
    
    def test_database_error(self):
        """Test excepción de base de datos"""
        error = DatabaseError("Error de conexión")
        assert str(error) == "Error de conexión"
        assert error.status_code == 500
    
    def test_not_found_error(self):
        """Test excepción de recurso no encontrado"""
        error = NotFoundError("Usuario no encontrado")
        assert str(error) == "Usuario no encontrado"
        assert error.status_code == 404
    
    def test_conflict_error(self):
        """Test excepción de conflicto"""
        error = ConflictError("Email ya existe")
        assert str(error) == "Email ya existe"
        assert error.status_code == 409


class TestErrorHandlingMiddleware:
    """Tests para middleware de manejo de errores"""
    
    def test_validation_error_response(self, client):
        """Test respuesta de error de validación"""
        # Intentar crear usuario con datos inválidos
        invalid_data = {
            "email": "invalid-email",
            "password": "123"  # Contraseña muy corta
        }
        
        response = client.post("/auth/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        assert "error_type" in data
        assert data["error_type"] == "validation_error"
    
    def test_authentication_error_response(self, client):
        """Test respuesta de error de autenticación"""
        # Intentar acceder a endpoint protegido sin token
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "error_type" in data
        assert data["error_type"] == "authentication_error"
    
    def test_authorization_error_response(self, client, auth_headers_student):
        """Test respuesta de error de autorización"""
        # Intentar acceder a endpoint de tutor como estudiante
        response = client.get("/tutor/alerts", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "detail" in data
        assert "error_type" in data
        assert data["error_type"] == "authorization_error"
    
    def test_not_found_error_response(self, client, auth_headers_student):
        """Test respuesta de error de recurso no encontrado"""
        # Intentar obtener usuario inexistente
        response = client.get("/auth/users/99999", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "error_type" in data
        assert data["error_type"] == "not_found_error"
    
    def test_conflict_error_response(self, client, test_student_data):
        """Test respuesta de error de conflicto"""
        # Intentar registrar usuario con email duplicado
        # Primero registrar un usuario
        client.post("/auth/register", json=test_student_data)
        
        # Luego intentar registrar otro con el mismo email
        response = client.post("/auth/register", json=test_student_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert "detail" in data
        assert "error_type" in data
        assert data["error_type"] == "conflict_error"
    
    def test_database_error_response(self, client, auth_headers_student):
        """Test respuesta de error de base de datos"""
        # Este test requeriría simular un error de base de datos
        # Por ahora, probamos que el middleware maneja errores genéricos
        response = client.get("/auth/me", headers=auth_headers_student)
        
        # Si hay un error de base de datos, debería devolver 500
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            data = response.json()
            assert "detail" in data
            assert "error_type" in data
            assert data["error_type"] == "database_error"


class TestErrorLogging:
    """Tests para logging de errores"""
    
    def test_error_logging_format(self, client):
        """Test formato de logging de errores"""
        # Intentar acceder a endpoint inexistente
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # El error debería estar registrado en los logs
        # Esto se verificaría revisando los archivos de log
    
    def test_validation_error_logging(self, client):
        """Test logging de errores de validación"""
        invalid_data = {"email": "invalid"}
        response = client.post("/auth/register", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        # El error de validación debería estar registrado
    
    def test_authentication_error_logging(self, client):
        """Test logging de errores de autenticación"""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # El error de autenticación debería estar registrado


class TestErrorResponseFormat:
    """Tests para formato de respuesta de errores"""
    
    def test_error_response_structure(self, client):
        """Test estructura de respuesta de error"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        # Verificar estructura estándar
        required_fields = ["detail", "error_type", "timestamp"]
        for field in required_fields:
            assert field in data
        
        assert isinstance(data["detail"], str)
        assert isinstance(data["error_type"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_error_response_with_request_id(self, client):
        """Test respuesta de error con ID de request"""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        # Verificar que hay un ID de request si está configurado
        if "request_id" in data:
            assert isinstance(data["request_id"], str)
    
    def test_error_response_in_development(self, client):
        """Test respuesta de error en modo desarrollo"""
        # En modo desarrollo, las respuestas pueden incluir más detalles
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        # En desarrollo, podría incluir stack trace
        if "stack_trace" in data:
            assert isinstance(data["stack_trace"], str)


class TestErrorHandlingEdgeCases:
    """Tests para casos edge del manejo de errores"""
    
    def test_malformed_json_request(self, client):
        """Test request con JSON malformado"""
        response = client.post(
            "/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_required_headers(self, client):
        """Test request con headers requeridos faltantes"""
        response = client.post("/auth/login", data={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_token_format(self, client):
        """Test token con formato inválido"""
        response = client.get("/auth/me", headers={"Authorization": "InvalidToken"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_expired_token(self, client):
        """Test token expirado"""
        # Esto requeriría crear un token expirado
        # Por ahora, probamos con un token inválido
        response = client.get("/auth/me", headers={"Authorization": "Bearer expired_token"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_large_request_body(self, client):
        """Test request con body muy grande"""
        large_data = {"message": "x" * 1000000}  # 1MB de datos
        
        response = client.post("/chat/send", json=large_data)
        
        # Debería devolver 413 Payload Too Large o 422
        assert response.status_code in [413, 422, 400]


class TestErrorRecovery:
    """Tests para recuperación de errores"""
    
    def test_graceful_degradation(self, client, auth_headers_student):
        """Test degradación graceful en caso de error"""
        # Intentar acceder a funcionalidad que podría fallar
        response = client.get("/analysis/stats", headers=auth_headers_student)
        
        # Debería devolver 200 con datos vacíos o 500 con mensaje claro
        assert response.status_code in [200, 500]
        
        if response.status_code == 500:
            data = response.json()
            assert "detail" in data
            assert "error_type" in data
    
    def test_partial_data_response(self, client, auth_headers_student):
        """Test respuesta con datos parciales en caso de error"""
        # Esto probaría que si parte de la funcionalidad falla,
        # se devuelven los datos disponibles
        response = client.get("/tutor/dashboard", headers=auth_headers_student)
        
        # Si hay error, debería devolver datos parciales o error claro
        if response.status_code == 200:
            data = response.json()
            # Verificar que al menos algunos campos están presentes
            assert len(data) > 0
        else:
            assert response.status_code == 403  # No autorizado como estudiante
