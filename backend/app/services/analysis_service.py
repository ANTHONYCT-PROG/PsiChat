from typing import List, Dict, Any, Optional
from app.models.emotion import predict_emotion, predict_all_emotions
from app.models.style import predict_style, predict_all_styles
from app.notifications.alerts import check_combined_alert
import json


def analyze_emotion(text: str) -> dict:
    dominant_emotion, score = predict_emotion(text)
    all_emotions = predict_all_emotions(text)
    return {
        "emotion": dominant_emotion,
        "emotion_score": score,
        "emotion_distribution": all_emotions
    }


def analyze_style(text: str) -> dict:
    dominant_style, score = predict_style(text)
    all_styles = predict_all_styles(text)
    return {
        "style": dominant_style,
        "style_score": score,
        "style_distribution": all_styles
    }


def evaluate_priority(emotion: str, emotion_score: float, style: str, style_score: float = 0.0, context_risk: str = "normal") -> str:
    """
    Evalúa la prioridad de atención basada en múltiples criterios:
    - Intensidad de emociones negativas
    - Estilos comunicativos de riesgo
    - Combinación de factores
    - Contexto de riesgo acumulativo
    
    Returns:
        str: "crítica", "alta", "media", "baja", "normal"
    """
    # Definir emociones de alto riesgo con sus umbrales específicos
    high_risk_emotions = {
        "frustración": 75,
        "tristeza": 80,
        "ansiedad": 70,
        "desánimo": 75,
        "ira": 70,
        "desesperación": 60,
        "soledad": 75
    }
    
    # Definir emociones de riesgo medio
    medium_risk_emotions = {
        "preocupación": 65,
        "confusión": 60,
        "inseguridad": 70,
        "nostalgia": 75
    }
    
    # Definir estilos de alto riesgo
    high_risk_styles = {
        "evasivo": 65,
        "pasivo-agresivo": 60,
        "agresivo": 55,
        "defensivo": 70
    }
    
    # Definir estilos de riesgo medio
    medium_risk_styles = {
        "formal": 80,
        "distante": 70,
        "sarcástico": 65
    }
    
    # Calcular puntuación de riesgo emocional
    emotion_risk_score = 0
    if emotion.lower() in high_risk_emotions:
        if emotion_score >= high_risk_emotions[emotion.lower()]:
            emotion_risk_score = 3  # Alto riesgo
        elif emotion_score >= high_risk_emotions[emotion.lower()] - 10:
            emotion_risk_score = 2  # Riesgo medio-alto
    elif emotion.lower() in medium_risk_emotions:
        if emotion_score >= medium_risk_emotions[emotion.lower()]:
            emotion_risk_score = 2  # Riesgo medio
        elif emotion_score >= medium_risk_emotions[emotion.lower()] - 15:
            emotion_risk_score = 1  # Riesgo bajo-medio
    
    # Calcular puntuación de riesgo de estilo
    style_risk_score = 0
    if style.lower() in high_risk_styles:
        if style_score >= high_risk_styles[style.lower()]:
            style_risk_score = 3  # Alto riesgo
        elif style_score >= high_risk_styles[style.lower()] - 10:
            style_risk_score = 2  # Riesgo medio-alto
    elif style.lower() in medium_risk_styles:
        if style_score >= medium_risk_styles[style.lower()]:
            style_risk_score = 2  # Riesgo medio
        elif style_score >= medium_risk_styles[style.lower()] - 15:
            style_risk_score = 1  # Riesgo bajo-medio
    
    # Calcular puntuación total de riesgo
    total_risk_score = emotion_risk_score + style_risk_score
    
    # Ajustar por contexto de riesgo acumulativo
    if context_risk == "alto":
        total_risk_score += 1
    elif context_risk == "medio":
        total_risk_score += 0.5
    
    # Casos especiales que elevan la prioridad
    special_cases = {
        "frustración": emotion_score >= 90,  # Frustración extrema
        "tristeza": emotion_score >= 95,     # Tristeza profunda
        "ansiedad": emotion_score >= 85,     # Ansiedad severa
        "desánimo": emotion_score >= 90,     # Desánimo profundo
    }
    
    # Verificar casos especiales
    for emotion_type, condition in special_cases.items():
        if emotion.lower() == emotion_type and condition:
            total_risk_score = max(total_risk_score, 4)  # Forzar prioridad crítica
    
    # Determinar prioridad final
    if total_risk_score >= 4:
        return "crítica"
    elif total_risk_score >= 3:
        return "alta"
    elif total_risk_score >= 2:
        return "media"
    elif total_risk_score >= 1:
        return "baja"
    else:
        return "normal"


def generate_recommendations(emotion: str, emotion_score: float, style: str, style_score: float, priority: str) -> Dict[str, List[str]]:
    """
    Genera recomendaciones personalizadas basadas en el análisis emocional y de estilo.
    """
    recommendations = {
        "immediate_actions": [],
        "emotional_support": [],
        "communication_tips": [],
        "long_term_suggestions": []
    }
    
    # Recomendaciones basadas en emoción
    if emotion == "tristeza":
        recommendations["immediate_actions"].append("Ofrecer empatía y validación emocional")
        recommendations["emotional_support"].append("Sugerir actividades que generen bienestar")
        recommendations["long_term_suggestions"].append("Considerar apoyo profesional si persiste")
    elif emotion == "ansiedad":
        recommendations["immediate_actions"].append("Ayudar con técnicas de respiración")
        recommendations["emotional_support"].append("Enfocarse en el momento presente")
        recommendations["communication_tips"].append("Usar un tono calmado y tranquilizador")
    elif emotion == "frustración":
        recommendations["immediate_actions"].append("Validar la frustración sin minimizarla")
        recommendations["emotional_support"].append("Ayudar a identificar soluciones")
        recommendations["communication_tips"].append("Mantener un enfoque constructivo")
    elif emotion == "alegría":
        recommendations["immediate_actions"].append("Celebrar y reforzar el estado positivo")
        recommendations["emotional_support"].append("Aprovechar el momento para establecer metas")
        recommendations["long_term_suggestions"].append("Documentar qué generó esta alegría")
    
    # Recomendaciones basadas en estilo
    if style == "evasivo":
        recommendations["communication_tips"].append("Crear un ambiente seguro para la expresión")
        recommendations["emotional_support"].append("Ser paciente y no presionar")
        recommendations["long_term_suggestions"].append("Trabajar en la confianza gradualmente")
    elif style == "agresivo":
        recommendations["immediate_actions"].append("Mantener calma y no responder con agresividad")
        recommendations["communication_tips"].append("Establecer límites claros y respetuosos")
        recommendations["emotional_support"].append("Ayudar a identificar las causas subyacentes")
    elif style == "formal":
        recommendations["communication_tips"].append("Mantener un tono profesional pero cálido")
        recommendations["emotional_support"].append("Respetar la preferencia por la formalidad")
    
    # Recomendaciones basadas en prioridad
    if priority == "crítica":
        recommendations["immediate_actions"].insert(0, "🚨 INTERVENCIÓN CRÍTICA REQUERIDA")
        recommendations["immediate_actions"].append("Contactar inmediatamente al tutor o profesional")
        recommendations["immediate_actions"].append("Evaluar necesidad de intervención de emergencia")
        recommendations["emotional_support"].append("Mantener presencia constante y apoyo inmediato")
        recommendations["long_term_suggestions"].append("Coordinar con servicios de salud mental")
    elif priority == "alta":
        recommendations["immediate_actions"].insert(0, "⚠️ ATENCIÓN INMEDIATA REQUERIDA")
        recommendations["immediate_actions"].append("Evaluar necesidad de intervención profesional")
        recommendations["emotional_support"].append("Mantener contacto frecuente y apoyo constante")
    elif priority == "media":
        recommendations["immediate_actions"].append("Monitorear cambios en el estado emocional")
        recommendations["emotional_support"].append("Ofrecer recursos de apoyo adicionales")
    elif priority == "baja":
        recommendations["immediate_actions"].append("Observar tendencias en el estado emocional")
        recommendations["emotional_support"].append("Ofrecer apoyo preventivo")
    
    return recommendations


def generate_summary(analysis: Dict[str, Any]) -> Dict[str, str]:
    """
    Genera un resumen ejecutivo del análisis.
    """
    emotion = analysis["emotion"]
    emotion_score = analysis["emotion_score"]
    style = analysis["style"]
    priority = analysis["priority"]
    alert = analysis["alert"]
    
    # Resumen ejecutivo
    if priority == "crítica":
        executive_summary = f"🚨 SITUACIÓN CRÍTICA: El usuario presenta {emotion} con intensidad del {emotion_score:.1f}% y estilo {style}. INTERVENCIÓN INMEDIATA REQUERIDA."
    elif priority == "alta":
        executive_summary = f"⚠️ SITUACIÓN DE ALTA PRIORIDAD: El usuario presenta {emotion} con intensidad del {emotion_score:.1f}% y estilo {style}. Requiere atención inmediata."
    elif priority == "media":
        executive_summary = f"📊 SITUACIÓN MODERADA: Estado emocional de {emotion} ({emotion_score:.1f}%) con estilo {style}. Monitoreo recomendado."
    elif priority == "baja":
        executive_summary = f"📈 SITUACIÓN DE BAJA PRIORIDAD: Estado emocional de {emotion} ({emotion_score:.1f}%) con estilo {style}. Observación preventiva."
    else:
        executive_summary = f"✅ ESTADO NORMAL: Emoción predominante {emotion} ({emotion_score:.1f}%) con estilo {style}. Continúa el apoyo regular."
    
    # Resumen técnico
    technical_summary = f"Análisis técnico: Emoción dominante '{emotion}' (confianza: {emotion_score:.1f}%), estilo comunicativo '{style}' (confianza: {analysis['style_score']:.1f}%). Prioridad: {priority}. Alerta: {'SÍ' if alert else 'NO'}."
    
    # Resumen para el usuario
    user_summary = f"Tu mensaje refleja principalmente {emotion} y un estilo de comunicación {style}. "
    if priority == "crítica":
        user_summary += "Es muy importante que sepas que estamos aquí para ayudarte. No dudes en buscar apoyo profesional si lo necesitas."
    elif priority == "alta":
        user_summary += "Es importante que sepas que estamos aquí para apoyarte."
    elif priority == "media":
        user_summary += "Recuerda que es normal tener altibajos emocionales."
    elif priority == "baja":
        user_summary += "Es bueno que mantengas esta comunicación abierta."
    else:
        user_summary += "Mantén esta comunicación abierta."
    
    return {
        "executive": executive_summary,
        "technical": technical_summary,
        "user_friendly": user_summary
    }


def analyze_chat_context(history: List[str]) -> Dict[str, Any]:
    """
    Analiza el historial completo del chat para detectar patrones acumulativos de riesgo.
    Returns:
        dict con resumen de emociones y estilos repetidos.
    """
    emotion_counter = {}
    style_counter = {}
    high_risk_count = 0

    for msg in history:
        emo, emo_score = predict_emotion(msg)
        style, style_score = predict_style(msg)

        emotion_counter[emo] = emotion_counter.get(emo, 0) + 1
        style_counter[style] = style_counter.get(style, 0) + 1

        if emo in ["frustración", "tristeza", "desánimo"] and emo_score >= 70:
            high_risk_count += 1

    context_flag = high_risk_count >= 2
    return {
        "emotion_frequency": emotion_counter,
        "style_frequency": style_counter,
        "context_alert": context_flag,
        "context_risk_level": "alto" if context_flag else "normal"
    }


def analyze_text(text: str, history: Optional[List[str]] = None) -> dict:
    """
    Analiza el texto individualmente, y opcionalmente el contexto (historial).
    """
    emotion_result = analyze_emotion(text)
    style_result = analyze_style(text)

    # Obtener contexto de riesgo si hay historial
    context_risk = "normal"
    if history:
        context_info = analyze_chat_context(history)
        context_risk = context_info.get("context_risk_level", "normal")
    
    priority = evaluate_priority(
        emotion_result["emotion"],
        emotion_result["emotion_score"],
        style_result["style"],
        style_result["style_score"],
        context_risk
    )

    alert_flag, alert_reason = check_combined_alert(
        emotion_result["emotion"],
        emotion_result["emotion_score"],
        style_result["style"],
        style_result["style_score"]
    )

    result = {
        "text": text,
        **emotion_result,
        **style_result,
        "priority": priority,
        "alert": alert_flag,
        "alert_reason": alert_reason if alert_flag else None,
    }

    if history:
        context_info = analyze_chat_context(history)
        result.update(context_info)

    return result

if __name__ == "__main__":
    history_msgs = [
        "¡Hola! Soy PsiChat, tu asistente emocional. ¿En qué puedo ayudarte hoy?"
    ]
    current = "ayer estube muy enojado porque me obligaron a irme de mi casa."
    full_result = analyze_text(current, history=history_msgs)

    print("=== Análisis con contexto ===")
    print(full_result)
