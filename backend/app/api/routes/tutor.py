"""
Rutas específicas para el panel de tutor.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.db.models import Usuario, Mensaje, Analisis, RolUsuario
from app.schemas.tutor import (
    AlertResponse, 
    StudentConversationResponse, 
    InterventionRequest,
    AlertReviewRequest
)
from app.api.routes.auth import get_current_user
from app.db import crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_tutor_access(current_user: Usuario = Depends(get_current_user)):
    """Verifica que el usuario actual sea un tutor."""
    if current_user.rol != RolUsuario.TUTOR:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo los tutores pueden acceder a esta funcionalidad."
        )
    return current_user

@router.get("/alerts", response_model=List[AlertResponse])
def get_student_alerts(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Obtiene todas las alertas emocionales de estudiantes.
    Solo para tutores.
    """
    try:
        # Obtener todos los estudiantes
        students = db.query(Usuario).filter(Usuario.rol == RolUsuario.ESTUDIANTE).all()
        alerts = []
        
        for student in students:
            # Obtener el último mensaje del estudiante
            last_message = db.query(Mensaje).filter(
                Mensaje.usuario_id == student.id
            ).order_by(Mensaje.creado_en.desc()).first()
            
            if last_message and last_message.analisis:
                # Determinar nivel de urgencia basado en el análisis
                urgencia = determinar_urgencia(last_message.analisis)
                
                # Solo incluir si hay una alerta significativa
                if urgencia != "leve" or last_message.analisis.alerta:
                    alerts.append({
                        "id": f"alert_{student.id}_{last_message.id}",
                        "student": {
                            "id": student.id,
                            "name": student.nombre or "Estudiante",
                            "email": student.email,
                            "avatar": "👩‍🎓" if student.nombre and "a" in student.nombre.lower() else "👨‍🎓"
                        },
                        "lastMessage": last_message.texto[:100] + "..." if len(last_message.texto) > 100 else last_message.texto,
                        "emotion": {
                            "name": last_message.analisis.emocion or "Neutral",
                            "icon": get_emotion_icon(last_message.analisis.emocion),
                            "score": last_message.analisis.emocion_score or 0.0
                        },
                        "urgency": urgencia,
                        "timestamp": last_message.creado_en.isoformat(),
                        "reviewed": False  # TODO: Implementar sistema de revisión
                    })
        
        # Ordenar por urgencia y timestamp
        alerts.sort(key=lambda x: (get_urgency_priority(x["urgency"]), x["timestamp"]), reverse=True)
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener alertas: {str(e)}"
        )

@router.get("/students")
def get_students(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Obtiene la lista de todos los estudiantes.
    Solo para tutores.
    """
    try:
        students = db.query(Usuario).filter(Usuario.rol == RolUsuario.ESTUDIANTE).all()
        
        student_list = []
        for student in students:
            # Obtener el último mensaje del estudiante
            last_message = db.query(Mensaje).filter(
                Mensaje.usuario_id == student.id
            ).order_by(Mensaje.creado_en.desc()).first()
            
            student_list.append({
                "id": student.id,
                "name": student.nombre or "Estudiante",
                "email": student.email,
                "avatar": "👩‍🎓" if student.nombre and "a" in student.nombre.lower() else "👨‍🎓",
                "last_message_time": last_message.creado_en.isoformat() if last_message else None,
                "status": "active" if last_message and (datetime.utcnow() - last_message.creado_en).days < 7 else "inactive"
            })
        
        return student_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estudiantes: {str(e)}"
        )

@router.get("/student/{student_id}/conversation", response_model=StudentConversationResponse)
def get_student_conversation(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Obtiene la conversación completa de un estudiante específico.
    Solo para tutores.
    """
    try:
        # Verificar que el estudiante existe
        student = db.query(Usuario).filter(
            Usuario.id == student_id,
            Usuario.rol == RolUsuario.ESTUDIANTE
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )
        
        # Obtener todos los mensajes del estudiante ordenados por fecha
        messages = db.query(Mensaje).filter(
            Mensaje.usuario_id == student_id
        ).order_by(Mensaje.creado_en.asc()).all()
        
        conversation = []
        for msg in messages:
            conversation.append({
                "id": msg.id,
                "sender": "student" if msg.remitente == "user" else "bot",
                "text": msg.texto,
                "emotion": msg.analisis.emocion if msg.analisis else "Neutral",
                "timestamp": msg.creado_en.strftime("%H:%M")
            })
        
        return {
            "student": {
                "id": student.id,
                "name": student.nombre or "Estudiante",
                "email": student.email,
                "avatar": "👩‍🎓" if student.nombre and "a" in student.nombre.lower() else "👨‍🎓"
            },
            "conversation": conversation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener conversación: {str(e)}"
        )

@router.get("/student/{student_id}/analysis")
def get_student_analysis(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Obtiene el análisis emocional de un estudiante específico.
    Solo para tutores.
    """
    try:
        # Verificar que el estudiante existe
        student = db.query(Usuario).filter(
            Usuario.id == student_id,
            Usuario.rol == RolUsuario.ESTUDIANTE
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )
        
        # Obtener todos los análisis del estudiante
        analyses = db.query(Analisis).join(Mensaje).filter(
            Mensaje.usuario_id == student_id
        ).order_by(Analisis.creado_en.desc()).all()
        
        if not analyses:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron análisis para este estudiante"
            )
        
        # Calcular estadísticas
        emotion_counts = {}
        style_counts = {}
        total_analyses = len(analyses)
        
        for analysis in analyses:
            if analysis.emocion:
                emotion_counts[analysis.emocion] = emotion_counts.get(analysis.emocion, 0) + 1
            if analysis.estilo:
                style_counts[analysis.estilo] = style_counts.get(analysis.estilo, 0) + 1
        
        # Obtener el análisis más reciente
        latest_analysis = analyses[0]
        
        return {
            "student": {
                "id": student.id,
                "name": student.nombre or "Estudiante",
                "email": student.email
            },
            "latest_analysis": {
                "emotion": latest_analysis.emocion,
                "emotion_score": latest_analysis.emocion_score,
                "style": latest_analysis.estilo,
                "style_score": latest_analysis.estilo_score,
                "priority": latest_analysis.prioridad,
                "alert": latest_analysis.alerta,
                "created_at": latest_analysis.creado_en.isoformat()
            },
            "statistics": {
                "total_analyses": total_analyses,
                "emotion_distribution": emotion_counts,
                "style_distribution": style_counts,
                "most_common_emotion": max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None,
                "most_common_style": max(style_counts.items(), key=lambda x: x[1])[0] if style_counts else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener análisis del estudiante: {str(e)}"
        )

@router.post("/intervene")
def send_intervention(
    intervention: InterventionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Envía una intervención del tutor a un estudiante.
    Solo para tutores.
    """
    try:
        # Verificar que el estudiante existe
        student = db.query(Usuario).filter(
            Usuario.id == intervention.student_id,
            Usuario.rol == RolUsuario.ESTUDIANTE
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=404,
                detail="Estudiante no encontrado"
            )
        
        # Crear mensaje de intervención del tutor
        intervention_message = Mensaje(
            usuario_id=intervention.student_id,
            texto=f"[INTERVENCIÓN TUTOR] {intervention.message}",
            remitente="tutor",
            creado_en=datetime.utcnow()
        )
        
        db.add(intervention_message)
        db.commit()
        
        return {
            "success": True,
            "message": "Intervención enviada exitosamente",
            "intervention_id": intervention_message.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar intervención: {str(e)}"
        )

@router.put("/alert/{alert_id}/review")
def mark_alert_as_reviewed(
    alert_id: str,
    review_data: AlertReviewRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Marca una alerta como revisada por el tutor.
    Solo para tutores.
    """
    try:
        # TODO: Implementar sistema de revisión de alertas
        # Por ahora, solo retornamos éxito
        return {
            "success": True,
            "message": "Alerta marcada como revisada",
            "alert_id": alert_id,
            "reviewed_by": current_user.id,
            "reviewed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al marcar alerta como revisada: {str(e)}"
        )

@router.post("/reports")
def generate_report(
    start_date: str,
    end_date: str,
    report_type: str = "general",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Genera un reporte de actividad de estudiantes.
    Solo para tutores.
    """
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Obtener mensajes en el rango de fechas
        messages = db.query(Mensaje).filter(
            Mensaje.creado_en >= start,
            Mensaje.creado_en <= end,
            Mensaje.remitente == "user"
        ).all()
        
        # Generar estadísticas básicas
        total_messages = len(messages)
        unique_students = len(set(msg.usuario_id for msg in messages))
        
        # Contar emociones
        emotion_counts = {}
        for msg in messages:
            if msg.analisis and msg.analisis.emocion:
                emotion_counts[msg.analisis.emocion] = emotion_counts.get(msg.analisis.emocion, 0) + 1
        
        return {
            "report_type": report_type,
            "period": {
                "start_date": start.isoformat(),
                "end_date": end.isoformat()
            },
            "statistics": {
                "total_messages": total_messages,
                "unique_students": unique_students,
                "emotion_distribution": emotion_counts,
                "average_messages_per_student": total_messages / unique_students if unique_students > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando reporte: {str(e)}"
        )

@router.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Obtiene las notificaciones del tutor.
    Solo para tutores.
    """
    try:
        # Por ahora, retornamos notificaciones simuladas
        # TODO: Implementar sistema de notificaciones real
        notifications = [
            {
                "id": 1,
                "type": "alert",
                "title": "Nueva alerta crítica",
                "message": "María González ha mostrado signos de estrés alto",
                "created_at": datetime.utcnow().isoformat(),
                "read": False
            },
            {
                "id": 2,
                "type": "intervention",
                "title": "Intervención enviada",
                "message": "Se envió una intervención a Carlos Rodríguez",
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "read": True
            }
        ]
        
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener notificaciones: {str(e)}"
        )

@router.put("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_tutor_access)
):
    """
    Marca una notificación como leída.
    Solo para tutores.
    """
    try:
        # TODO: Implementar sistema de notificaciones real
        return {
            "success": True,
            "message": "Notificación marcada como leída",
            "notification_id": notification_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al marcar notificación como leída: {str(e)}"
        )

# Funciones auxiliares
def determinar_urgencia(analisis: Analisis) -> str:
    """Determina el nivel de urgencia basado en el análisis emocional."""
    if analisis.alerta:
        return "crítico"
    
    if analisis.emocion_score and analisis.emocion_score > 0.8:
        return "crítico"
    elif analisis.emocion_score and analisis.emocion_score > 0.6:
        return "intermedio"
    else:
        return "leve"

def get_urgency_priority(urgency: str) -> int:
    """Retorna prioridad numérica para ordenamiento."""
    priorities = {
        "crítico": 3,
        "intermedio": 2,
        "leve": 1
    }
    return priorities.get(urgency, 0)

def get_emotion_icon(emotion: str) -> str:
    """Retorna el icono correspondiente a la emoción."""
    icons = {
        "Estrés": "😰",
        "Frustración": "😤",
        "Tristeza": "😢",
        "Confusión": "😕",
        "Alegría": "😊",
        "Enojo": "😠",
        "Miedo": "😨",
        "Sorpresa": "😲"
    }
    return icons.get(emotion, "😐") 