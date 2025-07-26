"""
Tests para el módulo de tutor
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestTutorAlerts:
    """Tests para alertas de tutores"""
    
    def test_get_alerts_success(self, client, auth_headers_tutor):
        """Test obtener alertas exitoso"""
        response = client.get("/tutor/alerts", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_alerts_as_student(self, client, auth_headers_student):
        """Test obtener alertas como estudiante (debe fallar)"""
        response = client.get("/tutor/alerts", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_alerts_no_auth(self, client):
        """Test obtener alertas sin autenticación"""
        response = client.get("/tutor/alerts")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_alerts_with_filters(self, client, auth_headers_tutor):
        """Test obtener alertas con filtros"""
        params = {
            "emotion": "tristeza",
            "priority": "alta",
            "status": "active"
        }
        
        response = client.get("/tutor/alerts", params=params, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_alert_by_id_success(self, client, auth_headers_tutor):
        """Test obtener alerta por ID exitoso"""
        # Primero obtener todas las alertas
        alerts_response = client.get("/tutor/alerts", headers=auth_headers_tutor)
        alerts = alerts_response.json()
        
        if alerts:
            alert_id = alerts[0]["id"]
            response = client.get(f"/tutor/alerts/{alert_id}", headers=auth_headers_tutor)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == alert_id
        else:
            # Si no hay alertas, probar con ID inexistente
            response = client.get("/tutor/alerts/99999", headers=auth_headers_tutor)
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_alert_by_id_not_found(self, client, auth_headers_tutor):
        """Test obtener alerta por ID inexistente"""
        response = client.get("/tutor/alerts/99999", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTutorInterventions:
    """Tests para intervenciones de tutores"""
    
    def test_send_intervention_success(self, client, auth_headers_tutor, test_student):
        """Test enviar intervención exitosa"""
        intervention_data = {
            "student_id": test_student.id,
            "message": "Hola, he notado que podrías necesitar apoyo. ¿Te gustaría hablar?",
            "intervention_type": "support"
        }
        
        response = client.post("/tutor/interventions", json=intervention_data, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["message"] == intervention_data["message"]
        assert data["student_id"] == test_student.id
    
    def test_send_intervention_as_student(self, client, auth_headers_student, test_tutor):
        """Test enviar intervención como estudiante (debe fallar)"""
        intervention_data = {
            "student_id": test_tutor.id,
            "message": "Test intervention",
            "intervention_type": "support"
        }
        
        response = client.post("/tutor/interventions", json=intervention_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_send_intervention_invalid_student(self, client, auth_headers_tutor):
        """Test enviar intervención a estudiante inexistente"""
        intervention_data = {
            "student_id": 99999,
            "message": "Test intervention",
            "intervention_type": "support"
        }
        
        response = client.post("/tutor/interventions", json=intervention_data, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_send_intervention_empty_message(self, client, auth_headers_tutor, test_student):
        """Test enviar intervención con mensaje vacío"""
        intervention_data = {
            "student_id": test_student.id,
            "message": "",
            "intervention_type": "support"
        }
        
        response = client.post("/tutor/interventions", json=intervention_data, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_interventions_history(self, client, auth_headers_tutor):
        """Test obtener historial de intervenciones"""
        response = client.get("/tutor/interventions", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_interventions_by_student(self, client, auth_headers_tutor, test_student):
        """Test obtener intervenciones por estudiante"""
        response = client.get(f"/tutor/interventions/student/{test_student.id}", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestTutorStudentManagement:
    """Tests para gestión de estudiantes por tutores"""
    
    def test_get_students_success(self, client, auth_headers_tutor):
        """Test obtener lista de estudiantes exitoso"""
        response = client.get("/tutor/students", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_students_as_student(self, client, auth_headers_student):
        """Test obtener estudiantes como estudiante (debe fallar)"""
        response = client.get("/tutor/students", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_student_details(self, client, auth_headers_tutor, test_student):
        """Test obtener detalles de estudiante"""
        response = client.get(f"/tutor/students/{test_student.id}", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_student.id
        assert "nombre" in data
        assert "email" in data
        assert "rol" in data
    
    def test_get_student_details_invalid_id(self, client, auth_headers_tutor):
        """Test obtener detalles de estudiante inexistente"""
        response = client.get("/tutor/students/99999", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_student_analysis(self, client, auth_headers_tutor, test_student):
        """Test obtener análisis de estudiante"""
        response = client.get(f"/tutor/students/{test_student.id}/analysis", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_student_chat_history(self, client, auth_headers_tutor, test_student):
        """Test obtener historial de chat de estudiante"""
        response = client.get(f"/tutor/students/{test_student.id}/chat", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestTutorStatistics:
    """Tests para estadísticas de tutores"""
    
    def test_get_tutor_stats_success(self, client, auth_headers_tutor):
        """Test obtener estadísticas de tutor exitoso"""
        response = client.get("/tutor/stats", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_students" in data
        assert "total_alerts" in data
        assert "total_interventions" in data
        assert "alerts_by_priority" in data
        assert "alerts_by_emotion" in data
    
    def test_get_tutor_stats_as_student(self, client, auth_headers_student):
        """Test obtener estadísticas como estudiante (debe fallar)"""
        response = client.get("/tutor/stats", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_tutor_stats_with_date_range(self, client, auth_headers_tutor):
        """Test obtener estadísticas con rango de fechas"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.get("/tutor/stats", params=params, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_students" in data


class TestTutorReports:
    """Tests para reportes de tutores"""
    
    def test_generate_report_success(self, client, auth_headers_tutor):
        """Test generar reporte exitoso"""
        report_data = {
            "report_type": "general",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "include_analysis": True,
            "include_chat": False
        }
        
        response = client.post("/tutor/reports", json=report_data, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "report_id" in data
        assert "status" in data
    
    def test_generate_report_as_student(self, client, auth_headers_student):
        """Test generar reporte como estudiante (debe fallar)"""
        report_data = {
            "report_type": "general",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.post("/tutor/reports", json=report_data, headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_report_status(self, client, auth_headers_tutor):
        """Test obtener estado de reporte"""
        # Primero generar un reporte
        report_data = {
            "report_type": "general",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        create_response = client.post("/tutor/reports", json=report_data, headers=auth_headers_tutor)
        report_id = create_response.json()["report_id"]
        
        # Luego verificar su estado
        response = client.get(f"/tutor/reports/{report_id}", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "report_id" in data
    
    def test_get_report_invalid_id(self, client, auth_headers_tutor):
        """Test obtener reporte con ID inválido"""
        response = client.get("/tutor/reports/99999", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_reports_list(self, client, auth_headers_tutor):
        """Test obtener lista de reportes"""
        response = client.get("/tutor/reports", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestTutorNotifications:
    """Tests para notificaciones de tutores"""
    
    def test_get_notifications_success(self, client, auth_headers_tutor):
        """Test obtener notificaciones exitoso"""
        response = client.get("/tutor/notifications", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_notifications_as_student(self, client, auth_headers_student):
        """Test obtener notificaciones como estudiante (debe fallar)"""
        response = client.get("/tutor/notifications", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_mark_notification_as_read(self, client, auth_headers_tutor):
        """Test marcar notificación como leída"""
        # Primero obtener notificaciones
        notifications_response = client.get("/tutor/notifications", headers=auth_headers_tutor)
        notifications = notifications_response.json()
        
        if notifications:
            notification_id = notifications[0]["id"]
            response = client.put(f"/tutor/notifications/{notification_id}/read", headers=auth_headers_tutor)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["read"] == True
        else:
            # Si no hay notificaciones, probar con ID inexistente
            response = client.put("/tutor/notifications/99999/read", headers=auth_headers_tutor)
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_mark_all_notifications_as_read(self, client, auth_headers_tutor):
        """Test marcar todas las notificaciones como leídas"""
        response = client.put("/tutor/notifications/read-all", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "updated_count" in data


class TestTutorDashboard:
    """Tests para dashboard de tutores"""
    
    def test_get_dashboard_data(self, client, auth_headers_tutor):
        """Test obtener datos del dashboard"""
        response = client.get("/tutor/dashboard", headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "stats" in data
        assert "recent_alerts" in data
        assert "recent_interventions" in data
        assert "students_summary" in data
    
    def test_get_dashboard_as_student(self, client, auth_headers_student):
        """Test obtener dashboard como estudiante (debe fallar)"""
        response = client.get("/tutor/dashboard", headers=auth_headers_student)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_dashboard_with_filters(self, client, auth_headers_tutor):
        """Test obtener dashboard con filtros"""
        params = {
            "time_range": "week",
            "include_inactive": False
        }
        
        response = client.get("/tutor/dashboard", params=params, headers=auth_headers_tutor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "stats" in data 