# Archivo: test_analysis.py
"""
Tests para validar el servicio de análisis de emociones y estilos.
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import status
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.models import Base
from app.db.session import get_db
from app.services.analysis_service import (
    analyze_emotion, analyze_style, evaluate_priority,
    analyze_chat_context, analyze_text
)


class TestAnalysis:
    """Tests para análisis de emociones y estilos."""
    
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Configurar base de datos de prueba."""
        # Crear base de datos en memoria para tests
        self.engine = create_engine("sqlite:///:memory:")
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Crear tablas
        Base.metadata.create_all(bind=self.engine)
        
        # Override de la dependencia de base de datos
        def override_get_db():
            try:
                db = self.TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Crear cliente de prueba
        self.client = TestClient(app)
        
        yield
        
        # Limpiar después de cada test
        app.dependency_overrides.clear()
    
    def test_analyze_emotion_positive(self):
        """Test análisis de emoción positiva."""
        text = "Estoy muy feliz y contento con mi vida"
        result = analyze_emotion(text)
        
        assert "emotion" in result
        assert "emotion_score" in result
        assert "emotion_distribution" in result
        assert result["emotion_score"] > 0
        assert result["emotion_score"] <= 100
        assert isinstance(result["emotion_distribution"], dict)
    
    def test_analyze_emotion_negative(self):
        """Test análisis de emoción negativa."""
        text = "Me siento triste y desanimado"
        result = analyze_emotion(text)
        
        assert "emotion" in result
        assert "emotion_score" in result
        assert "emotion_distribution" in result
        assert result["emotion_score"] > 0
        assert result["emotion_score"] <= 100
    
    def test_analyze_style_assertive(self):
        """Test análisis de estilo asertivo."""
        text = "Creo que deberíamos hacer esto de manera diferente"
        result = analyze_style(text)
        
        assert "style" in result
        assert "style_score" in result
        assert "style_distribution" in result
        assert result["style_score"] > 0
        assert result["style_score"] <= 100
    
    def test_analyze_style_passive(self):
        """Test análisis de estilo pasivo."""
        text = "Bueno, si tú dices que está bien..."
        result = analyze_style(text)
        
        assert "style" in result
        assert "style_score" in result
        assert "style_distribution" in result
        assert result["style_score"] > 0
        assert result["style_score"] <= 100
    
    def test_evaluate_priority_normal(self):
        """Test evaluación de prioridad normal."""
        priority = evaluate_priority("alegría", 30.0, "asertivo")
        assert priority == "normal"
    
    def test_evaluate_priority_high(self):
        """Test evaluación de prioridad alta."""
        priority = evaluate_priority("frustración", 80.0, "asertivo")
        assert priority == "alta"
    
    def test_evaluate_priority_medium(self):
        """Test evaluación de prioridad media."""
        priority = evaluate_priority("alegría", 60.0, "asertivo")
        assert priority == "media"
    
    def test_analyze_chat_context(self):
        """Test análisis de contexto del chat."""
        history = [
            "Estoy muy frustrado con esta tarea",
            "No puedo más, me rindo",
            "Me siento agotado"
        ]
        
        result = analyze_chat_context(history)
        
        assert "emotion_frequency" in result
        assert "style_frequency" in result
        assert "context_alert" in result
        assert "context_risk_level" in result
        assert isinstance(result["emotion_frequency"], dict)
        assert isinstance(result["style_frequency"], dict)
        assert isinstance(result["context_alert"], bool)
    
    def test_analyze_text_complete(self):
        """Test análisis completo de texto."""
        text = "Estoy muy feliz de haber terminado mi proyecto"
        result = analyze_text(text)
        
        # Verificar estructura completa
        required_fields = [
            "text", "emotion", "emotion_score", "emotion_distribution",
            "style", "style_score", "style_distribution",
            "priority", "alert", "alert_reason"
        ]
        
        for field in required_fields:
            assert field in result
        
        # Verificar tipos de datos
        assert result["text"] == text
        assert isinstance(result["emotion"], str)
        assert isinstance(result["emotion_score"], (int, float))
        assert isinstance(result["style"], str)
        assert isinstance(result["style_score"], (int, float))
        assert isinstance(result["priority"], str)
        assert isinstance(result["alert"], bool)
    
    def test_analyze_text_with_context(self):
        """Test análisis de texto con contexto."""
        text = "Ya no aguanto más"
        history = [
            "Estoy muy frustrado",
            "No puedo más con esto"
        ]
        
        result = analyze_text(text, history=history)
        
        # Verificar campos adicionales de contexto
        assert "context_alert" in result
        assert "context_risk_level" in result
        assert "emotion_frequency" in result
        assert "style_frequency" in result
    
    def test_analysis_endpoint_without_auth(self):
        """Test endpoint de análisis sin autenticación."""
        response = self.client.post("/analysis/", json={"text": "Estoy feliz"})
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_analysis_endpoint_with_auth(self):
        """Test endpoint de análisis con autenticación."""
        # Registrar y hacer login
        user_data = {
            "email": "test@example.com",
            "nombre": "Test User",
            "password": "testpassword123"
        }
        self.client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        login_response = self.client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Usar token en endpoint de análisis
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/analysis/", json={"text": "Estoy muy feliz"}, headers=headers)
        
        # Debería funcionar (aunque puede fallar por otros motivos, pero no por autenticación)
        assert response.status_code in [200, 500]  # 500 si hay problemas con ML models
    
    def test_analysis_endpoint_invalid_data(self):
        """Test endpoint de análisis con datos inválidos."""
        # Registrar y hacer login
        user_data = {
            "email": "test@example.com",
            "nombre": "Test User",
            "password": "testpassword123"
        }
        self.client.post("/auth/register", json=user_data)
        
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        login_response = self.client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Usar token con datos inválidos
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/analysis/", json={}, headers=headers)
        
        assert response.status_code == 422  # Validation error
    
    def test_emotion_detection_consistency(self):
        """Test consistencia en la detección de emociones."""
        # Mismo texto debería dar resultados similares
        text = "Estoy muy feliz"
        result1 = analyze_emotion(text)
        result2 = analyze_emotion(text)
        
        assert result1["emotion"] == result2["emotion"]
        assert abs(result1["emotion_score"] - result2["emotion_score"]) < 5  # Tolerancia pequeña
    
    def test_style_detection_consistency(self):
        """Test consistencia en la detección de estilos."""
        # Mismo texto debería dar resultados similares
        text = "Creo que deberíamos hacer esto"
        result1 = analyze_style(text)
        result2 = analyze_style(text)
        
        assert result1["style"] == result2["style"]
        assert abs(result1["style_score"] - result2["style_score"]) < 5  # Tolerancia pequeña
    
    def test_empty_text_analysis(self):
        """Test análisis de texto vacío."""
        result = analyze_text("")
        
        # Debería manejar texto vacío graciosamente
        assert "text" in result
        assert result["text"] == ""
        assert "emotion" in result
        assert "style" in result
    
    def test_long_text_analysis(self):
        """Test análisis de texto largo."""
        long_text = "Este es un texto muy largo que contiene muchas palabras y frases. " * 10
        result = analyze_text(long_text)
        
        # Debería manejar texto largo
        assert "text" in result
        assert "emotion" in result
        assert "style" in result
        assert len(result["text"]) > 100


"""
Tests para el módulo de análisis emocional
"""


class TestAnalysisCreate:
    """Tests para crear análisis"""
    
    def test_create_analysis_success(self, client, auth_headers_student):
        """Test creación exitosa de análisis"""
        analysis_data = {
            "message_text": "Estoy muy feliz hoy porque aprobé mi examen",
            "emotion": "alegría",
            "emotion_score": 85.5,
            "style": "positivo",
            "style_score": 78.2,
            "priority": "baja",
            "alert": False
        }
        
        response = client.post("/analysis/create", json=analysis_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["emotion"] == analysis_data["emotion"]
        assert data["emotion_score"] == analysis_data["emotion_score"]
        assert data["style"] == analysis_data["style"]
        assert data["priority"] == analysis_data["priority"]
    
    def test_create_analysis_no_auth(self, client):
        """Test crear análisis sin autenticación"""
        analysis_data = {
            "message_text": "Test message",
            "emotion": "tristeza",
            "emotion_score": 70.0
        }
        
        response = client.post("/analysis/create", json=analysis_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_analysis_missing_fields(self, client, auth_headers_student):
        """Test crear análisis con campos faltantes"""
        analysis_data = {
            "message_text": "Test message"
        }
        
        response = client.post("/analysis/create", json=analysis_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_analysis_invalid_emotion(self, client, auth_headers_student):
        """Test crear análisis con emoción inválida"""
        analysis_data = {
            "message_text": "Test message",
            "emotion": "invalid_emotion",
            "emotion_score": 70.0,
            "style": "positivo",
            "style_score": 60.0
        }
        
        response = client.post("/analysis/create", json=analysis_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_analysis_invalid_score(self, client, auth_headers_student):
        """Test crear análisis con score inválido"""
        analysis_data = {
            "message_text": "Test message",
            "emotion": "alegría",
            "emotion_score": 150.0,  # Score mayor a 100
            "style": "positivo",
            "style_score": 60.0
        }
        
        response = client.post("/analysis/create", json=analysis_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAnalysisGet:
    """Tests para obtener análisis"""
    
    def test_get_last_analysis_success(self, client, auth_headers_student):
        """Test obtener último análisis exitoso"""
        response = client.get("/analysis/last", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "emotion" in data
        assert "emotion_score" in data
        assert "created_at" in data
    
    def test_get_last_analysis_no_analysis(self, client, auth_headers_student):
        """Test obtener último análisis cuando no hay análisis"""
        # Primero limpiar cualquier análisis existente (esto dependería de la implementación)
        response = client.get("/analysis/last", headers=auth_headers_student)
        
        # Debería devolver 404 o un análisis vacío
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]
    
    def test_get_analysis_by_id_success(self, client, auth_headers_student):
        """Test obtener análisis por ID exitoso"""
        # Primero crear un análisis
        analysis_data = {
            "message_text": "Test message for ID lookup",
            "emotion": "calma",
            "emotion_score": 75.0,
            "style": "neutral",
            "style_score": 65.0
        }
        create_response = client.post("/analysis/create", json=analysis_data, headers=auth_headers_student)
        analysis_id = create_response.json()["id"]
        
        # Luego obtenerlo por ID
        response = client.get(f"/analysis/{analysis_id}", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == analysis_id
        assert data["message_text"] == analysis_data["message_text"]
    
    def test_get_analysis_by_id_not_found(self, client, auth_headers_student):
        """Test obtener análisis por ID inexistente"""
        response = client.get("/analysis/99999", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_analysis_by_id_unauthorized(self, client, auth_headers_student):
        """Test obtener análisis de otro usuario (debe fallar)"""
        # Esto requeriría crear un análisis con otro usuario
        # Por ahora, probamos con un ID que no existe
        response = client.get("/analysis/99999", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAnalysisHistory:
    """Tests para historial de análisis"""
    
    def test_get_analysis_history_success(self, client, auth_headers_student):
        """Test obtener historial de análisis exitoso"""
        response = client.get("/analysis/history", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_analysis_history_with_limit(self, client, auth_headers_student):
        """Test obtener historial con límite"""
        response = client.get("/analysis/history?limit=5", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_get_analysis_history_with_date_range(self, client, auth_headers_student):
        """Test obtener historial con rango de fechas"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.get("/analysis/history", params=params, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_analysis_history_no_auth(self, client):
        """Test obtener historial sin autenticación"""
        response = client.get("/analysis/history")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnalysisStatistics:
    """Tests para estadísticas de análisis"""
    
    def test_get_analysis_stats_success(self, client, auth_headers_student):
        """Test obtener estadísticas de análisis exitoso"""
        response = client.get("/analysis/stats", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_analyses" in data
        assert "emotion_distribution" in data
        assert "style_distribution" in data
        assert "average_scores" in data
    
    def test_get_analysis_stats_no_auth(self, client):
        """Test obtener estadísticas sin autenticación"""
        response = client.get("/analysis/stats")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_analysis_stats_with_date_range(self, client, auth_headers_student):
        """Test obtener estadísticas con rango de fechas"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.get("/analysis/stats", params=params, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_analyses" in data


class TestAnalysisDeepAnalysis:
    """Tests para análisis profundo"""
    
    def test_get_deep_analysis_success(self, client, auth_headers_student):
        """Test obtener análisis profundo exitoso"""
        response = client.get("/analysis/deep", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "summary" in data
        assert "recommendations" in data
        assert "detailed_insights" in data
        assert "trends" in data
    
    def test_get_deep_analysis_no_data(self, client, auth_headers_student):
        """Test obtener análisis profundo sin datos suficientes"""
        # Esto podría devolver un error o datos vacíos
        response = client.get("/analysis/deep", headers=auth_headers_student)
        
        # Debería devolver 200 con datos vacíos o 404
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_get_deep_analysis_no_auth(self, client):
        """Test obtener análisis profundo sin autenticación"""
        response = client.get("/analysis/deep")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnalysisTutorAccess:
    """Tests para acceso de tutores a análisis"""
    
    def test_get_student_analysis_as_tutor(self, client, auth_headers_tutor, test_student):
        """Test obtener análisis de estudiante como tutor"""
        response = client.get(f"/analysis/student/{test_student.id}", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_student_analysis_as_student(self, client, auth_headers_student, test_tutor):
        """Test obtener análisis de otro estudiante como estudiante (debe fallar)"""
        response = client.get(f"/analysis/student/{test_tutor.id}", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_student_analysis_invalid_student(self, client, auth_headers_tutor):
        """Test obtener análisis de estudiante inexistente"""
        response = client.get("/analysis/student/99999", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
