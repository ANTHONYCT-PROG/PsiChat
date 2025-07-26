# backend/app/api/routes/chat.py
"""
Rutas para el manejo del chat y análisis emocional del mensaje.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.chat_service import generate_bot_reply
from app.dependencies import get_current_user
from app.db.models import Usuario
from app.db import crud
from app.schemas.message import Message, MessageCreate
from app.schemas.analysis_record import AnalysisRecord
from fastapi import status
from app.services.analysis_service import analyze_text

router = APIRouter()

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    message: ChatMessage,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint principal de chat: analiza el mensaje del usuario,
    genera respuesta empática, responde al usuario y luego guarda los mensajes y análisis en segundo plano.
    """
    try:
        # 1. Generar análisis y respuesta del bot
        result = generate_bot_reply(user_text=message.user_text)
        meta = result["meta"]
        # 2. Guardar mensajes y análisis en segundo plano
        def guardar_historial():
            user_msg = crud.create_message(db, MessageCreate(
                usuario_id=int(current_user.id),
                texto=message.user_text,
                remitente="user"
            ))
            crud.create_analysis(db, AnalysisRecord(
                mensaje_id=int(user_msg.id),  # type: ignore
                emocion=meta.get("detected_emotion") or "",
                emocion_score=meta.get("emotion_score") or 0.0,
                estilo=meta.get("detected_style") or "",
                estilo_score=meta.get("style_score") or 0.0,
                prioridad=meta.get("priority") or "",
                alerta=meta.get("alert") if meta.get("alert") is not None else False,
                razon_alerta=meta.get("alert_reason") or ""
            ))
            bot_msg = crud.create_message(db, MessageCreate(
                usuario_id=int(current_user.id),
                texto=result["reply"],
                remitente="bot"
            ))
            crud.create_analysis(db, AnalysisRecord(
                mensaje_id=int(bot_msg.id),  # type: ignore
                emocion="",
                emocion_score=0.0,
                estilo="",
                estilo_score=0.0,
                prioridad="",
                alerta=False,
                razon_alerta=""
            ))
        background_tasks.add_task(guardar_historial)
        # 3. Responder al usuario inmediatamente
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/history", response_model=list[dict], status_code=status.HTTP_200_OK)
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Devuelve el historial de mensajes y análisis del usuario autenticado (últimos 20 mensajes).
    """
    mensajes = crud.get_messages_by_user(db, int(current_user.id), limit=20)
    history = []
    for msg in reversed(mensajes):  # Para mostrar en orden cronológico
        analisis = crud.get_analysis_by_message(db, int(msg.id))
        history.append({
            "id": msg.id,
            "content": msg.texto,
            "sender": msg.remitente,
            "timestamp": msg.creado_en.isoformat(),
            "emotion": analisis.emocion if analisis else None,
            "emotion_score": analisis.emocion_score if analisis else None,
            "style": analisis.estilo if analisis else None,
            "style_score": analisis.estilo_score if analisis else None,
            "priority": analisis.prioridad if analisis else None,
            "alert": analisis.alerta if analisis else None,
            "alert_reason": analisis.razon_alerta if analisis else None
        })
    return history

@router.post("/analysis", response_model=dict)
def analyze_message_endpoint(
    message: ChatMessage,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Analiza un mensaje individual y retorna el análisis emocional y de estilo detallado.
    """
    try:
        analysis = analyze_text(message.user_text)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")
