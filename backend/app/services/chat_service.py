# backend/app/services/chat_service.py

from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
import traceback

from app.services.analysis_service import analyze_text

# Configuración Gemini
api_key = "AIzaSyCMbhh8Prtt9Dn3wh8RBcV8dI5NZP3hjfs"  # API key proporcionada
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

def generate_bot_reply(user_text: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Genera una respuesta empática con análisis emocional y contexto del historial usando Gemini.
    """
    # --- 1. Preparar historial ---
    history = user_context.get("history", []) if user_context else []
    history_texts = [msg[0] for msg in history[-3:]]  # Últimos 3 mensajes del usuario

    # --- 2. Análisis emocional y de estilo con historial ---
    analysis = analyze_text(user_text, history=history_texts)

    # --- 3. Construir prompt personalizado ---
    system_prompt = (
        "Eres EmotiProfe, un tutor emocional para estudiantes. "
        "Tu objetivo es brindar respuestas empáticas, útiles y breves. "
        f"Actualmente, el usuario muestra la emoción '{analysis['emotion']}' con intensidad {analysis['emotion_score']}%, "
        f"y estilo '{analysis['style']}' ({analysis['style_score']}%).\n"
        "También se ha detectado un posible patrón de riesgo acumulado." if analysis.get("context_alert")
        else "Responde siempre en español, con amabilidad, comprensión y brevedad."
    )

    # --- 4. Construir mensajes para Gemini ---
    parts = [
        {"role": "user", "parts": [{"text": system_prompt}]}
    ]
    for user_msg, bot_msg in history[-3:]:
        parts.append({"role": "user", "parts": [{"text": user_msg}]})
        parts.append({"role": "model", "parts": [{"text": bot_msg}]})
    parts.append({"role": "user", "parts": [{"text": user_text}]})

    payload = {
        "contents": parts,
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30  # Aumentar timeout a 30 segundos
        )
        data = response.json()
        if response.status_code != 200:
            error_msg = data.get("error", {}).get("message", "Error desconocido de Gemini")
            return {
                "reply": f"[Gemini ERROR {response.status_code}] {error_msg}",
                "meta": {"timestamp": datetime.utcnow(), "error": error_msg},
                "history": history + [(user_text, f"[Gemini ERROR {response.status_code}] {error_msg}")]
            }
        # Gemini responde en 'candidates' -> 'content' -> 'parts' -> 'text'
        bot_reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        # --- 6. Preparar metadatos ---
        meta = {
            "timestamp": datetime.utcnow(),
            "detected_emotion": analysis["emotion"],
            "emotion_score": round(analysis["emotion_score"], 2),
            "detected_style": analysis["style"],
            "style_score": round(analysis["style_score"], 2),
            "priority": analysis["priority"],
            "alert": analysis["alert"],
            "alert_reason": analysis["alert_reason"],
            "context_alert": analysis.get("context_alert", False),
            "context_risk_level": analysis.get("context_risk_level", "normal"),
            "info": "Generado con Gemini 2.0 Flash + análisis emocional"
        }

        return {
            "reply": bot_reply,
            "meta": meta,
            "history": history + [(user_text, bot_reply)]
        }

    except Exception as e:
        return {
            "reply": f"[ERROR Gemini] {str(e)}\n{traceback.format_exc()}",
            "meta": {"timestamp": datetime.utcnow(), "error": str(e)},
            "history": history + [(user_text, f"[ERROR Gemini] {str(e)}")]
        }


if __name__ == "__main__":
    # Mensaje actual del usuario
    user_text = "No entiendo nada, estoy muy frustrado y quiero rendirme."

    # Historial de interacciones previas (solo textos del usuario y respuestas del bot)
    history = [
        ("Estoy cansado de no avanzar con mis tareas.", "Entiendo cómo te sientes. ¿Quieres que revisemos juntas la tarea?"),
        ("No tengo motivación para seguir hoy.", "Es válido sentirse así a veces. ¿Quieres que intentemos algo paso a paso?")
    ]

    user_context = {"history": history}

    # Llamar al chatbot con contexto
    result = generate_bot_reply(user_text, user_context)

    # Mostrar resultados
    print("=== Respuesta del chatbot ===")
    print("BOT:", result["reply"])
    print("\n=== Análisis emocional ===")
    for k, v in result["meta"].items():
        print(f"{k}: {v}")
