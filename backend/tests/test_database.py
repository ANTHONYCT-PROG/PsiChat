"""
Tests para el módulo de base de datos y operaciones CRUD
"""

import pytest
from sqlalchemy.orm import Session
from app.db import crud
from app.schemas.user import UserCreate
from app.schemas.message import MessageCreate
from app.schemas.analysis import AnalysisCreate
from app.db.models import RolUsuario, Usuario, Mensaje, Analisis
from datetime import datetime


class TestUserCRUD:
    """Tests para operaciones CRUD de usuarios"""
    
    def test_create_user_success(self, db_session: Session):
        """Test crear usuario exitoso"""
        user_data = UserCreate(
            email="test@example.com",
            nombre="Test User",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        user = crud.create_user(db_session, user_data)
        
        assert user.id is not None
        assert user.email == user_data.email
        assert user.nombre == user_data.nombre
        assert user.rol == user_data.rol
        assert user.hashed_password is not None
        assert user.hashed_password != user_data.password
    
    def test_create_user_duplicate_email(self, db_session: Session):
        """Test crear usuario con email duplicado"""
        user_data = UserCreate(
            email="duplicate@example.com",
            nombre="Test User",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        # Crear primer usuario
        crud.create_user(db_session, user_data)
        
        # Intentar crear segundo usuario con mismo email
        with pytest.raises(Exception):
            crud.create_user(db_session, user_data)
    
    def test_get_user_by_email_success(self, db_session: Session):
        """Test obtener usuario por email exitoso"""
        user_data = UserCreate(
            email="getbyemail@example.com",
            nombre="Test User",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        created_user = crud.create_user(db_session, user_data)
        retrieved_user = crud.get_user_by_email(db_session, user_data.email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == user_data.email
    
    def test_get_user_by_email_not_found(self, db_session: Session):
        """Test obtener usuario por email inexistente"""
        user = crud.get_user_by_email(db_session, "nonexistent@example.com")
        
        assert user is None
    
    def test_get_user_by_id_success(self, db_session: Session):
        """Test obtener usuario por ID exitoso"""
        user_data = UserCreate(
            email="getbyid@example.com",
            nombre="Test User",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        created_user = crud.create_user(db_session, user_data)
        retrieved_user = crud.get_user(db_session, created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == user_data.email
    
    def test_get_user_by_id_not_found(self, db_session: Session):
        """Test obtener usuario por ID inexistente"""
        user = crud.get_user(db_session, 99999)
        
        assert user is None
    
    def test_get_users_by_role(self, db_session: Session):
        """Test obtener usuarios por rol"""
        # Crear usuarios con diferentes roles
        student_data = UserCreate(
            email="student@example.com",
            nombre="Student",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        tutor_data = UserCreate(
            email="tutor@example.com",
            nombre="Tutor",
            apellido="Test",
            password="password123",
            rol=RolUsuario.TUTOR
        )
        
        crud.create_user(db_session, student_data)
        crud.create_user(db_session, tutor_data)
        
        # Obtener estudiantes
        students = crud.get_users_by_role(db_session, RolUsuario.ESTUDIANTE)
        assert len(students) >= 1
        assert all(user.rol == RolUsuario.ESTUDIANTE for user in students)
        
        # Obtener tutores
        tutors = crud.get_users_by_role(db_session, RolUsuario.TUTOR)
        assert len(tutors) >= 1
        assert all(user.rol == RolUsuario.TUTOR for user in tutors)
    
    def test_update_user_success(self, db_session: Session):
        """Test actualizar usuario exitoso"""
        user_data = UserCreate(
            email="update@example.com",
            nombre="Original Name",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        user = crud.create_user(db_session, user_data)
        
        # Actualizar nombre
        updated_user = crud.update_user(db_session, user.id, {"nombre": "Updated Name"})
        
        assert updated_user.nombre == "Updated Name"
        assert updated_user.email == user_data.email  # No debería cambiar
    
    def test_delete_user_success(self, db_session: Session):
        """Test eliminar usuario exitoso"""
        user_data = UserCreate(
            email="delete@example.com",
            nombre="Test User",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        user = crud.create_user(db_session, user_data)
        user_id = user.id
        
        # Eliminar usuario
        crud.delete_user(db_session, user_id)
        
        # Verificar que ya no existe
        deleted_user = crud.get_user(db_session, user_id)
        assert deleted_user is None


class TestMessageCRUD:
    """Tests para operaciones CRUD de mensajes"""
    
    def test_create_message_success(self, db_session: Session, test_student):
        """Test crear mensaje exitoso"""
        message_data = MessageCreate(
            content="Test message content",
            sender_id=test_student.id,
            receiver_id=test_student.id,  # Mensaje a sí mismo para prueba
            message_type="chat"
        )
        
        message = crud.create_message(db_session, message_data)
        
        assert message.id is not None
        assert message.content == message_data.content
        assert message.sender_id == test_student.id
        assert message.message_type == message_data.message_type
    
    def test_get_messages_by_user(self, db_session: Session, test_student):
        """Test obtener mensajes de un usuario"""
        # Crear varios mensajes
        for i in range(3):
            message_data = MessageCreate(
                content=f"Test message {i}",
                sender_id=test_student.id,
                receiver_id=test_student.id,
                message_type="chat"
            )
            crud.create_message(db_session, message_data)
        
        messages = crud.get_messages_by_user(db_session, test_student.id)
        
        assert len(messages) >= 3
        assert all(msg.sender_id == test_student.id or msg.receiver_id == test_student.id 
                  for msg in messages)
    
    def test_get_chat_history(self, db_session: Session, test_student, test_tutor):
        """Test obtener historial de chat entre dos usuarios"""
        # Crear mensajes entre estudiante y tutor
        for i in range(2):
            # Mensaje del estudiante al tutor
            message_data = MessageCreate(
                content=f"Student message {i}",
                sender_id=test_student.id,
                receiver_id=test_tutor.id,
                message_type="chat"
            )
            crud.create_message(db_session, message_data)
            
            # Mensaje del tutor al estudiante
            message_data = MessageCreate(
                content=f"Tutor message {i}",
                sender_id=test_tutor.id,
                receiver_id=test_student.id,
                message_type="chat"
            )
            crud.create_message(db_session, message_data)
        
        history = crud.get_chat_history(db_session, test_student.id, test_tutor.id)
        
        assert len(history) >= 4
        # Verificar que todos los mensajes son entre estos dos usuarios
        for msg in history:
            assert (msg.sender_id == test_student.id and msg.receiver_id == test_tutor.id) or \
                   (msg.sender_id == test_tutor.id and msg.receiver_id == test_student.id)


class TestAnalysisCRUD:
    """Tests para operaciones CRUD de análisis"""
    
    def test_create_analysis_success(self, db_session: Session, test_student):
        """Test crear análisis exitoso"""
        analysis_data = AnalysisCreate(
            user_id=test_student.id,
            message_text="Test message for analysis",
            emotion="alegría",
            emotion_score=85.5,
            style="positivo",
            style_score=78.2,
            priority="baja",
            alert=False
        )
        
        analysis = crud.create_analysis(db_session, analysis_data)
        
        assert analysis.id is not None
        assert analysis.user_id == test_student.id
        assert analysis.emotion == analysis_data.emotion
        assert analysis.emotion_score == analysis_data.emotion_score
        assert analysis.style == analysis_data.style
        assert analysis.priority == analysis_data.priority
    
    def test_get_last_analysis(self, db_session: Session, test_student):
        """Test obtener último análisis de un usuario"""
        # Crear varios análisis
        for i in range(3):
            analysis_data = AnalysisCreate(
                user_id=test_student.id,
                message_text=f"Test message {i}",
                emotion="tristeza",
                emotion_score=70.0 + i,
                style="negativo",
                style_score=60.0 + i,
                priority="media",
                alert=False
            )
            crud.create_analysis(db_session, analysis_data)
        
        last_analysis = crud.get_last_analysis(db_session, test_student.id)
        
        assert last_analysis is not None
        assert last_analysis.user_id == test_student.id
        # El último análisis debería tener el score más alto
        assert last_analysis.emotion_score == 72.0
    
    def test_get_analysis_history(self, db_session: Session, test_student):
        """Test obtener historial de análisis"""
        # Crear varios análisis
        for i in range(5):
            analysis_data = AnalysisCreate(
                user_id=test_student.id,
                message_text=f"Test message {i}",
                emotion="calma",
                emotion_score=75.0,
                style="neutral",
                style_score=65.0,
                priority="baja",
                alert=False
            )
            crud.create_analysis(db_session, analysis_data)
        
        history = crud.get_analysis_history(db_session, test_student.id, limit=3)
        
        assert len(history) == 3
        assert all(analysis.user_id == test_student.id for analysis in history)
    
    def test_get_analysis_statistics(self, db_session: Session, test_student):
        """Test obtener estadísticas de análisis"""
        # Crear análisis con diferentes emociones
        emotions = ["alegría", "tristeza", "calma", "ansiedad"]
        for i, emotion in enumerate(emotions):
            analysis_data = AnalysisCreate(
                user_id=test_student.id,
                message_text=f"Test message {i}",
                emotion=emotion,
                emotion_score=70.0 + i * 5,
                style="positivo",
                style_score=60.0,
                priority="baja",
                alert=False
            )
            crud.create_analysis(db_session, analysis_data)
        
        stats = crud.get_analysis_statistics(db_session, test_student.id)
        
        assert "total_analyses" in stats
        assert "emotion_distribution" in stats
        assert "style_distribution" in stats
        assert "average_scores" in stats
        assert stats["total_analyses"] >= 4


class TestDatabaseRelationships:
    """Tests para relaciones entre tablas"""
    
    def test_user_messages_relationship(self, db_session: Session, test_student):
        """Test relación usuario-mensajes"""
        # Crear mensajes para el usuario
        for i in range(3):
            message_data = MessageCreate(
                content=f"Test message {i}",
                sender_id=test_student.id,
                receiver_id=test_student.id,
                message_type="chat"
            )
            crud.create_message(db_session, message_data)
        
        # Obtener usuario con mensajes
        user = crud.get_user(db_session, test_student.id)
        
        # Verificar que los mensajes están relacionados
        assert len(user.mensajes_enviados) >= 3
        assert all(msg.sender_id == test_student.id for msg in user.mensajes_enviados)
    
    def test_user_analysis_relationship(self, db_session: Session, test_student):
        """Test relación usuario-análisis"""
        # Crear análisis para el usuario
        for i in range(3):
            analysis_data = AnalysisCreate(
                user_id=test_student.id,
                message_text=f"Test message {i}",
                emotion="alegría",
                emotion_score=75.0,
                style="positivo",
                style_score=65.0,
                priority="baja",
                alert=False
            )
            crud.create_analysis(db_session, analysis_data)
        
        # Obtener usuario con análisis
        user = crud.get_user(db_session, test_student.id)
        
        # Verificar que los análisis están relacionados
        assert len(user.analisis) >= 3
        assert all(analysis.user_id == test_student.id for analysis in user.analisis)
    
    def test_cascade_delete_user(self, db_session: Session):
        """Test eliminación en cascada de usuario"""
        # Crear usuario con mensajes y análisis
        user_data = UserCreate(
            email="cascade@example.com",
            nombre="Cascade User",
            apellido="Test",
            password="password123",
            rol=RolUsuario.ESTUDIANTE
        )
        
        user = crud.create_user(db_session, user_data)
        
        # Crear mensajes
        for i in range(2):
        message_data = MessageCreate(
                content=f"Test message {i}",
                sender_id=user.id,
                receiver_id=user.id,
                message_type="chat"
            )
            crud.create_message(db_session, message_data)
        
        # Crear análisis
        for i in range(2):
            analysis_data = AnalysisCreate(
                user_id=user.id,
                message_text=f"Test message {i}",
                emotion="alegría",
                emotion_score=75.0,
                style="positivo",
                style_score=65.0,
                priority="baja",
                alert=False
            )
            crud.create_analysis(db_session, analysis_data)
        
        user_id = user.id
        
        # Eliminar usuario
        crud.delete_user(db_session, user_id)
        
        # Verificar que los mensajes y análisis también se eliminaron
        messages = crud.get_messages_by_user(db_session, user_id)
        assert len(messages) == 0
        
        analysis = crud.get_last_analysis(db_session, user_id)
        assert analysis is None 