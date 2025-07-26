"""
Tests para el módulo de autenticación
"""

import pytest
from fastapi import status
from app.db.models import RolUsuario
from app.schemas.user import UserCreate


class TestAuthRegistration:
    """Tests para el registro de usuarios"""
    
    def test_register_student_success(self, client, test_student_data):
        """Test registro exitoso de estudiante"""
        response = client.post("/auth/register", json=test_student_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_student_data["email"]
        assert data["nombre"] == test_student_data["nombre"]
        assert data["rol"] == test_student_data["rol"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_tutor_success(self, client, test_tutor_data):
        """Test registro exitoso de tutor"""
        response = client.post("/auth/register", json=test_tutor_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rol"] == RolUsuario.TUTOR
    
    def test_register_duplicate_email(self, client, test_student_data, test_student):
        """Test registro con email duplicado"""
        response = client.post("/auth/register", json=test_student_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ya está registrado" in response.json()["detail"]
    
    def test_register_invalid_email(self, client, test_student_data):
        """Test registro con email inválido"""
        test_student_data["email"] = "invalid-email"
        response = client.post("/auth/register", json=test_student_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client, test_student_data):
        """Test registro con contraseña corta"""
        test_student_data["password"] = "123"
        response = client.post("/auth/register", json=test_student_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_required_fields(self, client):
        """Test registro con campos faltantes"""
        response = client.post("/auth/register", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLogin:
    """Tests para el login de usuarios"""
    
    def test_login_success(self, client, test_student_data, test_student):
        """Test login exitoso"""
        response = client.post("/auth/login", data={
            "username": test_student_data["email"],
            "password": test_student_data["password"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_student_data["email"]
    
    def test_login_invalid_credentials(self, client, test_student_data):
        """Test login con credenciales inválidas"""
        response = client.post("/auth/login", data={
            "username": test_student_data["email"],
            "password": "wrong_password"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrectas" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login con usuario inexistente"""
        response = client.post("/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_credentials(self, client):
        """Test login sin credenciales"""
        response = client.post("/auth/login", data={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthCurrentUser:
    """Tests para obtener usuario actual"""
    
    def test_get_current_user_success(self, client, auth_headers_student):
        """Test obtener usuario actual exitoso"""
        response = client.get("/auth/me", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "nombre" in data
        assert "rol" in data
    
    def test_get_current_user_no_token(self, client):
        """Test obtener usuario actual sin token"""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Test obtener usuario actual con token inválido"""
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthUsersByRole:
    """Tests para obtener usuarios por rol"""
    
    def test_get_students_as_tutor(self, client, auth_headers_tutor, test_student):
        """Test obtener estudiantes como tutor"""
        response = client.get("/auth/students", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_students_as_student(self, client, auth_headers_student):
        """Test obtener estudiantes como estudiante (debe fallar)"""
        response = client.get("/auth/students", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_users_by_role_as_tutor(self, client, auth_headers_tutor):
        """Test obtener usuarios por rol como tutor"""
        response = client.get("/auth/users/estudiante", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_users_by_role_as_student(self, client, auth_headers_student):
        """Test obtener usuarios por rol como estudiante (debe fallar)"""
        response = client.get("/auth/users/tutor", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthRoleDetermination:
    """Tests para la determinación automática de roles"""
    
    def test_role_determination_educational_email(self, client):
        """Test determinación de rol para email educativo"""
        student_data = {
            "email": "profesor@edu.co",
            "nombre": "Profesor Test",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=student_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rol"] == RolUsuario.TUTOR
    
    def test_role_determination_regular_email(self, client):
        """Test determinación de rol para email regular"""
        student_data = {
            "email": "estudiante@gmail.com",
            "nombre": "Estudiante Test",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=student_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rol"] == RolUsuario.ESTUDIANTE
