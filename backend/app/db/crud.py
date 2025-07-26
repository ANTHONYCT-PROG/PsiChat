"""
Funciones CRUD para todas las entidades de la base de datos con manejo robusto de errores.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import json

from app.db import models
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.message import MessageCreate
from app.schemas.analysis_record import AnalysisRecord
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError
from app.core.logging import logger, log_database_operation
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== USUARIOS ====================

@log_database_operation
def get_user_by_email(db: Session, email: str) -> Optional[models.Usuario]:
    """Obtiene un usuario por email."""
    try:
        return db.query(models.Usuario).filter(models.Usuario.email == email).first()
    except SQLAlchemyError as e:
        logger.error("Error al obtener usuario por email", error=e, data={"email": email})
        raise DatabaseError("Error al buscar usuario por email")


@log_database_operation
def get_user(db: Session, user_id: int) -> Optional[models.Usuario]:
    """Obtiene un usuario por ID."""
    try:
        return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error("Error al obtener usuario por ID", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al buscar usuario")


@log_database_operation
def get_users_by_role(db: Session, rol: models.RolUsuario, limit: int = 100) -> List[models.Usuario]:
    """Obtiene usuarios por rol."""
    try:
        return db.query(models.Usuario).filter(
            models.Usuario.rol == rol,
            models.Usuario.estado == models.EstadoUsuario.ACTIVO
        ).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener usuarios por rol", error=e, data={"rol": rol})
        raise DatabaseError("Error al buscar usuarios por rol")


@log_database_operation
def create_user(db: Session, user: UserCreate) -> models.Usuario:
    """Crea un nuevo usuario."""
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = models.Usuario(
            email=user.email,
            nombre=user.nombre,
            apellido=user.apellido,
            hashed_password=hashed_password,
            rol=user.rol,
            telefono=user.telefono,
            fecha_nacimiento=user.fecha_nacimiento,
            genero=user.genero,
            institucion=user.institucion,
            grado_academico=user.grado_academico,
            configuraciones=user.configuraciones
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info("Usuario creado exitosamente", data={"user_id": db_user.id, "email": db_user.email})
        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error("Error de integridad al crear usuario", error=e, data={"email": user.email})
        raise ValidationError("El email ya está registrado")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear usuario", error=e, data={"email": user.email})
        raise DatabaseError("Error al crear usuario")


@log_database_operation
def update_user(db: Session, user_id: int, user_update: UserUpdate) -> models.Usuario:
    """Actualiza un usuario existente."""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            raise NotFoundError("Usuario")
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.actualizado_en = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
        logger.info("Usuario actualizado exitosamente", data={"user_id": user_id})
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al actualizar usuario", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al actualizar usuario")


@log_database_operation
def update_user_last_access(db: Session, user_id: int) -> None:
    """Actualiza el último acceso del usuario."""
    try:
        db_user = get_user(db, user_id)
        if db_user:
            db_user.ultimo_acceso = datetime.utcnow()
            db.commit()
    except SQLAlchemyError as e:
        logger.error("Error al actualizar último acceso", error=e, data={"user_id": user_id})


@log_database_operation
def delete_user(db: Session, user_id: int) -> bool:
    """Elimina un usuario (soft delete)."""
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            raise NotFoundError("Usuario")
        
        db_user.estado = models.EstadoUsuario.INACTIVO
        db.commit()
        logger.info("Usuario eliminado exitosamente", data={"user_id": user_id})
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al eliminar usuario", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al eliminar usuario")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña."""
    return pwd_context.verify(plain_password, hashed_password)


def determinar_rol_por_email(email: str) -> models.RolUsuario:
    """
    Determina el rol del usuario basándose en el dominio del email.
    Emails con dominios educativos o específicos serán tutores.
    """
    # Lista de dominios que indican tutores/docentes
    dominios_tutor = [
        "edu.co", "edu.mx", "edu.ar", "edu.cl", "edu.pe", "edu.ec", "edu.ve",
        "edu.bo", "edu.py", "edu.uy", "edu.gt", "edu.hn", "edu.ni", "edu.cr",
        "edu.pa", "edu.do", "edu.cu", "edu.pr", "profesor", "teacher", "docente",
        "tutor", "instructor"
    ]
    
    email_lower = email.lower()
    for dominio in dominios_tutor:
        if dominio in email_lower:
            return models.RolUsuario.TUTOR
    
    return models.RolUsuario.ESTUDIANTE


# ==================== MENSAJES ====================

@log_database_operation
def create_message(db: Session, message: MessageCreate) -> models.Mensaje:
    """Crea un nuevo mensaje."""
    try:
        db_message = models.Mensaje(**message.model_dump())
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        logger.info("Mensaje creado exitosamente", data={"message_id": db_message.id, "user_id": db_message.usuario_id})
        return db_message
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear mensaje", error=e, data={"user_id": message.usuario_id})
        raise DatabaseError("Error al crear mensaje")


@log_database_operation
def get_messages_by_user(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[models.Mensaje]:
    """Obtiene mensajes de un usuario."""
    try:
        return db.query(models.Mensaje).filter(
            models.Mensaje.usuario_id == user_id
        ).order_by(desc(models.Mensaje.creado_en)).offset(offset).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener mensajes del usuario", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al obtener mensajes")


@log_database_operation
def get_chat_history(db: Session, user_id: int, limit: int = 20) -> List[models.Mensaje]:
    """Obtiene el historial de chat de un usuario."""
    try:
        return db.query(models.Mensaje).filter(
            models.Mensaje.usuario_id == user_id
        ).order_by(asc(models.Mensaje.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener historial de chat", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al obtener historial de chat")


@log_database_operation
def get_message_count_by_user(db: Session, user_id: int) -> int:
    """Obtiene el número total de mensajes de un usuario."""
    try:
        return db.query(models.Mensaje).filter(models.Mensaje.usuario_id == user_id).count()
    except SQLAlchemyError as e:
        logger.error("Error al contar mensajes del usuario", error=e, data={"user_id": user_id})
        return 0


# ==================== ANÁLISIS ====================

@log_database_operation
def create_analysis(db: Session, record: AnalysisRecord) -> models.Analisis:
    """Crea un nuevo análisis."""
    try:
        db_analysis = models.Analisis(**record.model_dump())
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        logger.info("Análisis creado exitosamente", data={"analysis_id": db_analysis.id, "user_id": db_analysis.usuario_id})
        return db_analysis
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear análisis", error=e, data={"user_id": record.usuario_id})
        raise DatabaseError("Error al crear análisis")


@log_database_operation
def get_analysis_by_message(db: Session, mensaje_id: int) -> Optional[models.Analisis]:
    """Obtiene análisis por mensaje."""
    try:
        return db.query(models.Analisis).filter(models.Analisis.mensaje_id == mensaje_id).first()
    except SQLAlchemyError as e:
        logger.error("Error al obtener análisis por mensaje", error=e, data={"mensaje_id": mensaje_id})
        raise DatabaseError("Error al obtener análisis")


@log_database_operation
def get_last_analysis_by_user(db: Session, user_id: int) -> Optional[models.Analisis]:
    """Obtiene el último análisis de un usuario."""
    try:
        return db.query(models.Analisis).filter(
            models.Analisis.usuario_id == user_id
        ).order_by(desc(models.Analisis.creado_en)).first()
    except SQLAlchemyError as e:
        logger.error("Error al obtener último análisis del usuario", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al obtener último análisis")


@log_database_operation
def get_analysis_history(db: Session, user_id: int, limit: int = 10) -> List[models.Analisis]:
    """Obtiene el historial de análisis de un usuario."""
    try:
        return db.query(models.Analisis).filter(
            models.Analisis.usuario_id == user_id
        ).order_by(desc(models.Analisis.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener historial de análisis", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al obtener historial de análisis")


@log_database_operation
def get_analyses_with_alerts(db: Session, limit: int = 50) -> List[models.Analisis]:
    """Obtiene análisis con alertas."""
    try:
        return db.query(models.Analisis).filter(
            models.Analisis.alerta == True
        ).order_by(desc(models.Analisis.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener análisis con alertas", error=e)
        raise DatabaseError("Error al obtener análisis con alertas")


# ==================== NOTIFICACIONES ====================

@log_database_operation
def create_notification(db: Session, user_id: int, titulo: str, mensaje: str, tipo: str, metadata: Dict = None) -> models.Notificacion:
    """Crea una nueva notificación."""
    try:
        db_notification = models.Notificacion(
            usuario_id=user_id,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            metadata=metadata
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        logger.info("Notificación creada exitosamente", data={"notification_id": db_notification.id, "user_id": user_id})
        return db_notification
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear notificación", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al crear notificación")


@log_database_operation
def get_user_notifications(db: Session, user_id: int, limit: int = 50, unread_only: bool = False) -> List[models.Notificacion]:
    """Obtiene notificaciones de un usuario."""
    try:
        query = db.query(models.Notificacion).filter(models.Notificacion.usuario_id == user_id)
        if unread_only:
            query = query.filter(models.Notificacion.leida == False)
        return query.order_by(desc(models.Notificacion.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener notificaciones del usuario", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al obtener notificaciones")


@log_database_operation
def mark_notification_as_read(db: Session, notification_id: int) -> bool:
    """Marca una notificación como leída."""
    try:
        notification = db.query(models.Notificacion).filter(models.Notificacion.id == notification_id).first()
        if notification:
            notification.leida = True
            notification.leida_en = datetime.utcnow()
            db.commit()
            logger.info("Notificación marcada como leída", data={"notification_id": notification_id})
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al marcar notificación como leída", error=e, data={"notification_id": notification_id})
        raise DatabaseError("Error al marcar notificación como leída")


# ==================== ALERTAS ====================

@log_database_operation
def create_alert(db: Session, user_id: int, analisis_id: int, tipo_alerta: str, nivel_urgencia: str, descripcion: str) -> models.Alerta:
    """Crea una nueva alerta."""
    try:
        db_alert = models.Alerta(
            usuario_id=user_id,
            analisis_id=analisis_id,
            tipo_alerta=tipo_alerta,
            nivel_urgencia=nivel_urgencia,
            descripcion=descripcion
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        logger.info("Alerta creada exitosamente", data={"alert_id": db_alert.id, "user_id": user_id})
        return db_alert
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear alerta", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al crear alerta")


@log_database_operation
def get_alerts(db: Session, limit: int = 50, unread_only: bool = False, nivel_urgencia: str = None) -> List[models.Alerta]:
    """Obtiene alertas con filtros opcionales."""
    try:
        query = db.query(models.Alerta)
        if unread_only:
            query = query.filter(models.Alerta.revisada == False)
        if nivel_urgencia:
            query = query.filter(models.Alerta.nivel_urgencia == nivel_urgencia)
        return query.order_by(desc(models.Alerta.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener alertas", error=e)
        raise DatabaseError("Error al obtener alertas")


@log_database_operation
def mark_alert_as_reviewed(db: Session, alert_id: int, tutor_id: int, notas: str = None, accion_tomada: str = None) -> bool:
    """Marca una alerta como revisada."""
    try:
        alert = db.query(models.Alerta).filter(models.Alerta.id == alert_id).first()
        if alert:
            alert.revisada = True
            alert.tutor_asignado = tutor_id
            alert.notas_tutor = notas
            alert.accion_tomada = accion_tomada
            alert.revisada_en = datetime.utcnow()
            db.commit()
            logger.info("Alerta marcada como revisada", data={"alert_id": alert_id, "tutor_id": tutor_id})
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al marcar alerta como revisada", error=e, data={"alert_id": alert_id})
        raise DatabaseError("Error al marcar alerta como revisada")


# ==================== INTERVENCIONES ====================

@log_database_operation
def create_intervention(db: Session, usuario_id: int, tutor_id: int, tipo_intervencion: str, mensaje: str, alerta_id: int = None, metodo: str = None) -> models.Intervencion:
    """Crea una nueva intervención."""
    try:
        db_intervention = models.Intervencion(
            usuario_id=usuario_id,
            tutor_id=tutor_id,
            alerta_id=alerta_id,
            tipo_intervencion=tipo_intervencion,
            mensaje=mensaje,
            metodo=metodo
        )
        db.add(db_intervention)
        db.commit()
        db.refresh(db_intervention)
        logger.info("Intervención creada exitosamente", data={"intervention_id": db_intervention.id, "user_id": usuario_id})
        return db_intervention
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear intervención", error=e, data={"user_id": usuario_id})
        raise DatabaseError("Error al crear intervención")


@log_database_operation
def get_user_interventions(db: Session, user_id: int, limit: int = 50) -> List[models.Intervencion]:
    """Obtiene intervenciones de un usuario."""
    try:
        return db.query(models.Intervencion).filter(
            models.Intervencion.usuario_id == user_id
        ).order_by(desc(models.Intervencion.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener intervenciones del usuario", error=e, data={"user_id": user_id})
        raise DatabaseError("Error al obtener intervenciones")


# ==================== MÉTRICAS ====================

@log_database_operation
def create_metric(db: Session, tipo_metrica: str, nombre: str, valor: float, unidad: str = None, contexto: Dict = None) -> models.Metricas:
    """Crea una nueva métrica."""
    try:
        db_metric = models.Metricas(
            tipo_metrica=tipo_metrica,
            nombre=nombre,
            valor=valor,
            unidad=unidad,
            contexto=contexto
        )
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error al crear métrica", error=e, data={"tipo_metrica": tipo_metrica, "nombre": nombre})
        raise DatabaseError("Error al crear métrica")


@log_database_operation
def get_metrics_by_type(db: Session, tipo_metrica: str, limit: int = 100) -> List[models.Metricas]:
    """Obtiene métricas por tipo."""
    try:
        return db.query(models.Metricas).filter(
            models.Metricas.tipo_metrica == tipo_metrica
        ).order_by(desc(models.Metricas.creado_en)).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error("Error al obtener métricas por tipo", error=e, data={"tipo_metrica": tipo_metrica})
        raise DatabaseError("Error al obtener métricas")
