# backend/app/api/routes/analysis.py
"""
Rutas para análisis emocional y comunicativo del texto.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.message import MessageCreate
from app.schemas.analysis import AnalysisResult
from app.services.analysis_service import analyze_text, generate_recommendations, generate_summary
from app.dependencies import get_current_user
from app.db.models import Usuario, Analisis, Mensaje
from sqlalchemy import desc

router = APIRouter()

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AnalysisResult)
def analyze_endpoint(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint que analiza un mensaje de texto:
    - Detecta emoción dominante y distribución
    - Detecta estilo dominante y distribución
    - Evalúa prioridad y alerta emocional
    """
    try:
        result = analyze_text(message.texto)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


@router.post("/complete")
def analyze_complete_endpoint(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para análisis completo del último mensaje:
    - Análisis emocional y de estilo detallado
    - Recomendaciones personalizadas
    - Resumen ejecutivo
    - Evaluación de riesgo
    """
    try:
        # Análisis básico
        basic_analysis = analyze_text(message.texto)
        
        # Generar recomendaciones
        recommendations = generate_recommendations(
            basic_analysis["emotion"],
            basic_analysis["emotion_score"],
            basic_analysis["style"],
            basic_analysis["style_score"],
            basic_analysis["priority"]
        )
        
        # Generar resumen
        summary = generate_summary(basic_analysis)
        
        # Análisis completo
        complete_analysis = {
            **basic_analysis,
            "recommendations": recommendations,
            "summary": summary,
            "detailed_insights": {
                "emotional_state": f"El usuario muestra un estado emocional de {basic_analysis['emotion']} con una intensidad del {basic_analysis['emotion_score']:.1f}%",
                "communication_style": f"Su estilo de comunicación es {basic_analysis['style']} con una confianza del {basic_analysis['style_score']:.1f}%",
                "risk_assessment": f"Nivel de prioridad: {basic_analysis['priority']}",
                "alert_status": "Requiere atención inmediata" if basic_analysis['alert'] else "Estado normal"
            }
        }
        
        # Guardar el análisis en la base de datos con las distribuciones
        # Primero buscar o crear el mensaje
        mensaje = db.query(Mensaje).filter(
            Mensaje.usuario_id == current_user.id,
            Mensaje.texto == message.texto,
            Mensaje.remitente == "user"
        ).order_by(desc(Mensaje.creado_en)).first()
        
        if mensaje:
            # Crear o actualizar el análisis
            analisis = db.query(Analisis).filter(Analisis.mensaje_id == mensaje.id).first()
            if not analisis:
                analisis = Analisis(mensaje_id=mensaje.id)
            
            # Actualizar datos del análisis
            analisis.emocion = basic_analysis["emotion"]
            analisis.emocion_score = basic_analysis["emotion_score"]
            analisis.estilo = basic_analysis["style"]
            analisis.estilo_score = basic_analysis["style_score"]
            analisis.prioridad = basic_analysis["priority"]
            analisis.alerta = basic_analysis["alert"]
            analisis.razon_alerta = basic_analysis.get("alert_reason")
            
            # Guardar distribuciones como JSON
            analisis.distribucion_emociones = json.dumps(basic_analysis.get("emotion_distribution", []))
            analisis.distribucion_estilos = json.dumps(basic_analysis.get("style_distribution", []))
            
            db.add(analisis)
            db.commit()
        
        return complete_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis completo: {str(e)}")


@router.get("/last")
def get_last_analysis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para obtener el último análisis realizado por el usuario actual.
    Retorna el análisis completo con recomendaciones y resumen.
    """
    try:
        # Buscar el último mensaje del usuario que tenga un análisis asociado
        last_message_with_analysis = db.query(Mensaje).join(Analisis).filter(
            Mensaje.usuario_id == current_user.id,
            Mensaje.remitente == "user"  # Solo mensajes del usuario, no del bot
        ).order_by(desc(Mensaje.creado_en)).first()
        
        if not last_message_with_analysis:
            raise HTTPException(status_code=404, detail="No se encontraron análisis previos del usuario")
        
        # Obtener el análisis asociado
        last_analysis = last_message_with_analysis.analisis
        
        if not last_analysis:
            raise HTTPException(status_code=404, detail="No se encontró análisis para el último mensaje")
        
        # Reconstruir el análisis completo
        basic_analysis = {
            "emotion": last_analysis.emocion,
            "emotion_score": last_analysis.emocion_score,
            "style": last_analysis.estilo,
            "style_score": last_analysis.estilo_score,
            "priority": last_analysis.prioridad,
            "alert": last_analysis.alerta,
            "alert_reason": last_analysis.razon_alerta,
            "emotion_distribution": json.loads(last_analysis.distribucion_emociones) if last_analysis.distribucion_emociones else [],
            "style_distribution": json.loads(last_analysis.distribucion_estilos) if last_analysis.distribucion_estilos else [],
            "text": last_message_with_analysis.texto  # <-- Aseguramos que el texto del mensaje esté presente
        }
        
        # Generar recomendaciones
        recommendations = generate_recommendations(
            basic_analysis["emotion"],
            basic_analysis["emotion_score"],
            basic_analysis["style"],
            basic_analysis["style_score"],
            basic_analysis["priority"]
        )
        
        # Generar resumen
        summary = generate_summary(basic_analysis)
        
        # Análisis completo
        complete_analysis = {
            **basic_analysis,
            "recommendations": recommendations,
            "summary": summary,
            "detailed_insights": {
                "emotional_state": f"El usuario muestra un estado emocional de {basic_analysis['emotion']} con una intensidad del {basic_analysis['emotion_score']:.1f}%",
                "communication_style": f"Su estilo de comunicación es {basic_analysis['style']} con una confianza del {basic_analysis['style_score']:.1f}%",
                "risk_assessment": f"Nivel de prioridad: {basic_analysis['priority']}",
                "alert_status": "Requiere atención inmediata" if basic_analysis['alert'] else "Estado normal"
            },
            "message_text": last_message_with_analysis.texto,
            "analysis_date": last_analysis.creado_en.isoformat()
        }
        
        return complete_analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el último análisis: {str(e)}")


@router.get("/history")
def get_analysis_history(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    limit: int = 10
):
    """
    Endpoint para obtener el historial de análisis del usuario actual.
    """
    try:
        # Buscar los últimos análisis del usuario (solo mensajes del usuario, no del bot)
        analyses = db.query(Analisis).join(Mensaje).filter(
            Mensaje.usuario_id == current_user.id,
            Mensaje.remitente == "user"  # Solo mensajes del usuario
        ).order_by(desc(Analisis.creado_en)).limit(limit).all()
        
        history = []
        for analysis in analyses:
            history.append({
                "id": analysis.id,
                "emotion": analysis.emocion,
                "emotion_score": analysis.emocion_score,
                "style": analysis.estilo,
                "style_score": analysis.estilo_score,
                "priority": analysis.prioridad,
                "alert": analysis.alerta,
                "created_at": analysis.creado_en.isoformat(),
                "message_text": analysis.mensaje.texto[:100] + "..." if len(analysis.mensaje.texto) > 100 else analysis.mensaje.texto
            })
        
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el historial: {str(e)}")


@router.get("/deep")
def deep_analysis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para análisis profundo de los últimos 10 mensajes del usuario.
    - Limpieza completa de texto
    - Análisis individual y promedio
    - Datos para gráficos (radar, barras, tabla)
    """
    import re
    from app.services.analysis_service import analyze_text

    # 1. Recuperar los últimos 10 mensajes del usuario (solo remitente 'user')
    mensajes = db.query(Mensaje).filter(
        Mensaje.usuario_id == current_user.id,
        Mensaje.remitente == "user"
    ).order_by(desc(Mensaje.creado_en)).limit(10).all()

    if not mensajes:
        raise HTTPException(status_code=404, detail="No hay mensajes para analizar.")

    # 2. Limpieza completa de texto
    def limpiar_texto(texto):
        texto = texto.lower()
        texto = re.sub(r"[^a-záéíóúüñ0-9\s]", "", texto)  # Solo letras/números/espacios
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    mensajes_limpios = [limpiar_texto(m.texto) for m in mensajes]

    # 3. Analizar cada mensaje individualmente
    analisis_individual = [analyze_text(texto) for texto in mensajes_limpios]

    # 4. Calcular promedios de scores para emociones y estilos
    # Obtener todas las emociones y estilos posibles
    all_emotions = set()
    all_styles = set()
    for a in analisis_individual:
        for emo, _ in a["emotion_distribution"]:
            all_emotions.add(emo)
        for sty, _ in a["style_distribution"]:
            all_styles.add(sty)
    all_emotions = sorted(list(all_emotions))
    all_styles = sorted(list(all_styles))

    # Promedio de scores
    avg_emotions = {emo: 0 for emo in all_emotions}
    avg_styles = {sty: 0 for sty in all_styles}
    for a in analisis_individual:
        emo_dict = dict(a["emotion_distribution"])
        sty_dict = dict(a["style_distribution"])
        for emo in all_emotions:
            avg_emotions[emo] += emo_dict.get(emo, 0)
        for sty in all_styles:
            avg_styles[sty] += sty_dict.get(sty, 0)
    for emo in avg_emotions:
        avg_emotions[emo] = round(avg_emotions[emo] / len(analisis_individual), 2)
    for sty in avg_styles:
        avg_styles[sty] = round(avg_styles[sty] / len(analisis_individual), 2)

    # 5. Preparar datos para gráficos
    # Radar: promedios
    radar_data = {
        "emotions": avg_emotions,
        "styles": avg_styles
    }
    # Barras: evolución por mensaje
    barras_emociones = []
    barras_estilos = []
    for idx, a in enumerate(analisis_individual):
        barras_emociones.append({"mensaje": idx+1, **dict(a["emotion_distribution"])})
        barras_estilos.append({"mensaje": idx+1, **dict(a["style_distribution"])})

    # Tabla: detalle por mensaje
    tabla = []
    for idx, (m, a) in enumerate(zip(mensajes, analisis_individual)):
        tabla.append({
            "mensaje": m.texto,
            "limpio": mensajes_limpios[idx],
            "emocion": a["emotion"],
            "emocion_score": a["emotion_score"],
            "estilo": a["style"],
            "estilo_score": a["style_score"],
            "distribucion_emociones": a["emotion_distribution"],
            "distribucion_estilos": a["style_distribution"]
        })

    # Insights automáticos
    insights = {
        "emocion_mas_frecuente": max(avg_emotions, key=avg_emotions.get),
        "estilo_mas_frecuente": max(avg_styles, key=avg_styles.get),
        "emocion_mas_alta": max(tabla, key=lambda x: x["emocion_score"])["emocion"],
        "estilo_mas_alto": max(tabla, key=lambda x: x["estilo_score"])["estilo"]
    }

    # Preparar datos para el frontend
    average_emotion_distribution = [{"emotion": emo, "score": score/100} for emo, score in avg_emotions.items()]
    average_style_distribution = [{"style": sty, "score": score/100} for sty, score in avg_styles.items()]
    
    # Generar tendencias emocionales
    emotion_trends = []
    emotion_counts = {}
    for a in analisis_individual:
        emotion = a["emotion"]
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    for emotion, count in emotion_counts.items():
        emotion_trends.append({
            "emotion": emotion,
            "frequency": count,
            "description": f"Esta emoción apareció en {count} de {len(analisis_individual)} mensajes analizados."
        })
    
    # Generar tendencias de estilos
    style_trends = []
    style_counts = {}
    for a in analisis_individual:
        style = a["style"]
        style_counts[style] = style_counts.get(style, 0) + 1
    
    for style, count in style_counts.items():
        style_trends.append({
            "style": style,
            "frequency": count,
            "description": f"Este estilo de comunicación apareció en {count} de {len(analisis_individual)} mensajes analizados."
        })
    
    # Generar insights y recomendaciones
    insights = [
        f"Tu emoción más frecuente es '{insights['emocion_mas_frecuente']}' con un promedio del {avg_emotions[insights['emocion_mas_frecuente']]:.1f}%",
        f"Tu estilo de comunicación predominante es '{insights['estilo_mas_frecuente']}' con un promedio del {avg_styles[insights['estilo_mas_frecuente']]:.1f}%",
        f"La emoción más intensa detectada fue '{insights['emocion_mas_alta']}'",
        f"El estilo de comunicación más marcado fue '{insights['estilo_mas_alto']}'"
    ]
    
    recommendations = [
        "Considera practicar técnicas de respiración si detectas altos niveles de ansiedad",
        "Mantén un diario emocional para identificar patrones en tus estados de ánimo",
        "Practica la comunicación asertiva para mejorar tus interacciones",
        "Busca apoyo profesional si notas patrones emocionales preocupantes"
    ]
    
    return {
        "average_emotion_distribution": average_emotion_distribution,
        "average_style_distribution": average_style_distribution,
        "emotion_trends": emotion_trends,
        "style_trends": style_trends,
        "insights": insights,
        "recommendations": recommendations,
        "message_count": len(mensajes),
        "analysis_date": mensajes[0].creado_en.isoformat() if mensajes else None
    }
