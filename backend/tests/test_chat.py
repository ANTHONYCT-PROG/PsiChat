"""
Tests para el módulo de chat
"""

import pytest
from fastapi import status
from datetime import datetime


class TestChatSendMessage:
    """Tests para enviar mensajes"""
    
    def test_send_message_success(self, client, auth_headers_student):
        """Test envío exitoso de mensaje"""
        message_data = {
            "user_text": "Hola, ¿cómo estás?",
            "history": []
        }
        
        response = client.post("/chat/send", json=message_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reply" in data
        assert "meta" in data
        assert "detected_emotion" in data["meta"]
        assert "detected_style" in data["meta"]
    
    def test_send_message_with_history(self, client, auth_headers_student):
        """Test envío de mensaje con historial"""
        message_data = {
            "user_text": "Estoy preocupado por mi examen",
            "history": [
                ["Hola", "¡Hola! ¿En qué puedo ayudarte?"],
                ["Tengo un examen mañana", "Entiendo que estés nervioso. ¿Qué te preocupa específicamente?"]
            ]
        }
        
        response = client.post("/chat/send", json=message_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reply" in data
    
    def test_send_message_no_auth(self, client):
        """Test envío de mensaje sin autenticación"""
        message_data = {
            "user_text": "Hola",
            "history": []
        }
        
        response = client.post("/chat/send", json=message_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_send_empty_message(self, client, auth_headers_student):
        """Test envío de mensaje vacío"""
        message_data = {
            "user_text": "",
            "history": []
        }
        
        response = client.post("/chat/send", json=message_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_send_message_missing_fields(self, client, auth_headers_student):
        """Test envío de mensaje con campos faltantes"""
        response = client.post("/chat/send", json={}, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestChatHistory:
    """Tests para el historial de chat"""
    
    def test_get_chat_history_success(self, client, auth_headers_student):
        """Test obtener historial de chat exitoso"""
        response = client.get("/chat/history", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_chat_history_no_auth(self, client):
        """Test obtener historial sin autenticación"""
        response = client.get("/chat/history")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_chat_history_with_limit(self, client, auth_headers_student):
        """Test obtener historial con límite"""
        response = client.get("/chat/history?limit=5", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


class TestDirectChat:
    """Tests para chat directo entre usuarios"""
    
    def test_send_direct_message_success(self, client, auth_headers_student, test_tutor):
        """Test envío exitoso de mensaje directo"""
        message_data = {
            "content": "Hola tutor, necesito ayuda",
            "receiver_id": test_tutor.id
        }
        
        response = client.post("/chat/direct/send", json=message_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["content"] == message_data["content"]
        assert data["receiver_id"] == test_tutor.id
    
    def test_send_direct_message_invalid_receiver(self, client, auth_headers_student):
        """Test envío de mensaje directo a receptor inválido"""
        message_data = {
            "content": "Hola",
            "receiver_id": 99999
        }
        
        response = client.post("/chat/direct/send", json=message_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_direct_chat_history(self, client, auth_headers_student, test_tutor):
        """Test obtener historial de chat directo"""
        response = client.get(f"/chat/direct/{test_tutor.id}", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_direct_chat_history_invalid_user(self, client, auth_headers_student):
        """Test obtener historial de chat directo con usuario inválido"""
        response = client.get("/chat/direct/99999", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestChatSessions:
    """Tests para sesiones de chat"""
    
    def test_create_chat_session(self, client, auth_headers_student):
        """Test crear sesión de chat"""
        session_data = {
            "title": "Sesión de prueba",
            "description": "Descripción de prueba"
        }
        
        response = client.post("/chat/sessions", json=session_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["title"] == session_data["title"]
    
    def test_get_chat_sessions(self, client, auth_headers_student):
        """Test obtener sesiones de chat"""
        response = client.get("/chat/sessions", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_chat_session_by_id(self, client, auth_headers_student):
        """Test obtener sesión de chat por ID"""
        # Primero crear una sesión
        session_data = {"title": "Test Session"}
        create_response = client.post("/chat/sessions", json=session_data, headers=auth_headers_student)
        session_id = create_response.json()["id"]
        
        # Luego obtenerla
        response = client.get(f"/chat/sessions/{session_id}", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == session_id
    
    def test_get_chat_session_invalid_id(self, client, auth_headers_student):
        """Test obtener sesión de chat con ID inválido"""
        response = client.get("/chat/sessions/99999", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestChatAnalytics:
    """Tests para analytics de chat"""
    
    def test_get_chat_analytics(self, client, auth_headers_student):
        """Test obtener analytics de chat"""
        response = client.get("/chat/analytics", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_messages" in data
        assert "total_sessions" in data
        assert "avg_messages_per_session" in data
    
    def test_get_chat_analytics_no_auth(self, client):
        """Test obtener analytics sin autenticación"""
        response = client.get("/chat/analytics")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_chat_analytics_with_date_range(self, client, auth_headers_student):
        """Test obtener analytics con rango de fechas"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.get("/chat/analytics", params=params, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_messages" in data
