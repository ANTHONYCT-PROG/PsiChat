# Archivo: test_alerts.py
"""
Tests para validar el módulo de evaluación de alertas emocionales.
"""

import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.notifications.alerts import (
    is_emotion_alert,
    is_style_alert,
    check_emotion_alert,
    check_combined_alert,
    EMOTION_THRESHOLDS,
    STYLE_RISKY,
    EMOTION_RISKY
)


class TestAlerts:
    """Tests para el módulo de alertas emocionales."""
    
    def test_emotion_thresholds_defined(self):
        """Test que verifica que los umbrales de emociones estén definidos."""
        assert isinstance(EMOTION_THRESHOLDS, dict)
        assert len(EMOTION_THRESHOLDS) > 0
        
        # Verificar que todas las emociones de riesgo estén en los umbrales
        for emotion in EMOTION_RISKY:
            assert emotion in EMOTION_THRESHOLDS
    
    def test_style_risky_defined(self):
        """Test que verifica que los estilos riesgosos estén definidos."""
        assert isinstance(STYLE_RISKY, set)
        assert len(STYLE_RISKY) > 0
        
        # Verificar que todos los estilos riesgosos estén en EMOTION_RISKY
        for style in STYLE_RISKY:
            assert isinstance(style, str)
    
    def test_is_emotion_alert_below_threshold(self):
        """Test que verifica que no se active alerta cuando el score está por debajo del umbral."""
        # Test con frustración (umbral 70)
        assert not is_emotion_alert("frustración", 50.0)
        assert not is_emotion_alert("frustración", 69.9)
        assert not is_emotion_alert("FRUSTRACIÓN", 50.0)  # Case insensitive
    
    def test_is_emotion_alert_at_threshold(self):
        """Test que verifica que se active alerta cuando el score está en el umbral."""
        # Test con frustración (umbral 70)
        assert is_emotion_alert("frustración", 70.0)
        assert is_emotion_alert("frustración", 80.0)
        assert is_emotion_alert("FRUSTRACIÓN", 70.0)  # Case insensitive
    
    def test_is_emotion_alert_above_threshold(self):
        """Test que verifica que se active alerta cuando el score está por encima del umbral."""
        # Test con diferentes emociones
        assert is_emotion_alert("tristeza", 75.0)  # Umbral 70
        assert is_emotion_alert("ansiedad", 70.0)  # Umbral 65
        assert is_emotion_alert("desánimo", 65.0)  # Umbral 60
    
    def test_is_emotion_alert_unknown_emotion(self):
        """Test que verifica que no se active alerta para emociones no definidas."""
        assert not is_emotion_alert("alegría", 90.0)
        assert not is_emotion_alert("sorpresa", 80.0)
        assert not is_emotion_alert("", 100.0)
        assert not is_emotion_alert(None, 100.0)
    
    def test_is_style_alert_below_threshold(self):
        """Test que verifica que no se active alerta de estilo cuando el score está por debajo del umbral."""
        # Umbral para estilos es 60
        assert not is_style_alert("evasivo", 50.0)
        assert not is_style_alert("pasivo-agresivo", 59.9)
        assert not is_style_alert("irónico", 30.0)
    
    def test_is_style_alert_at_threshold(self):
        """Test que verifica que se active alerta de estilo cuando el score está en el umbral."""
        # Umbral para estilos es 60
        assert is_style_alert("evasivo", 60.0)
        assert is_style_alert("pasivo-agresivo", 70.0)
        assert is_style_alert("irónico", 80.0)
        assert is_style_alert("EVASIVO", 60.0)  # Case insensitive
    
    def test_is_style_alert_above_threshold(self):
        """Test que verifica que se active alerta de estilo cuando el score está por encima del umbral."""
        assert is_style_alert("evasivo", 75.0)
        assert is_style_alert("pasivo-agresivo", 85.0)
        assert is_style_alert("irónico", 90.0)
    
    def test_is_style_alert_safe_style(self):
        """Test que verifica que no se active alerta para estilos seguros."""
        assert not is_style_alert("asertivo", 90.0)
        assert not is_style_alert("empático", 80.0)
        assert not is_style_alert("", 100.0)
        assert not is_style_alert(None, 100.0)
    
    def test_check_emotion_alert_no_alert(self):
        """Test que verifica que no se active alerta emocional cuando no corresponde."""
        alert, reason = check_emotion_alert("alegría", 50.0)
        assert not alert
        assert reason == ""
        
        alert, reason = check_emotion_alert("frustración", 60.0)  # Por debajo del umbral
        assert not alert
        assert reason == ""
    
    def test_check_emotion_alert_with_alert(self):
        """Test que verifica que se active alerta emocional cuando corresponde."""
        alert, reason = check_emotion_alert("frustración", 80.0)
        assert alert
        assert "frustración" in reason.lower()
        assert "80" in reason
        
        alert, reason = check_emotion_alert("tristeza", 75.0)
        assert alert
        assert "tristeza" in reason.lower()
        assert "75" in reason
    
    def test_check_emotion_alert_case_insensitive(self):
        """Test que verifica que la detección de alerta sea case insensitive."""
        alert, reason = check_emotion_alert("FRUSTRACIÓN", 80.0)
        assert alert
        assert "frustración" in reason.lower()
        
        alert, reason = check_emotion_alert("Tristeza", 75.0)
        assert alert
        assert "tristeza" in reason.lower()
    
    def test_check_combined_alert_no_alerts(self):
        """Test que verifica que no se active alerta combinada cuando no hay alertas."""
        alert, reason = check_combined_alert("alegría", 50.0, "asertivo", 40.0)
        assert not alert
        assert reason == ""
        
        alert, reason = check_combined_alert("frustración", 60.0, "asertivo", 50.0)  # Ambos por debajo
        assert not alert
        assert reason == ""
    
    def test_check_combined_alert_emotion_only(self):
        """Test que verifica que se active alerta solo por emoción."""
        alert, reason = check_combined_alert("frustración", 80.0, "asertivo", 40.0)
        assert alert
        assert "frustración" in reason.lower()
        assert "80" in reason
        assert "umbral" in reason.lower()
    
    def test_check_combined_alert_style_only(self):
        """Test que verifica que se active alerta solo por estilo."""
        alert, reason = check_combined_alert("alegría", 50.0, "evasivo", 70.0)
        assert alert
        assert "evasivo" in reason.lower()
        assert "70" in reason
        assert "evasión" in reason.lower() or "tensión" in reason.lower()
    
    def test_check_combined_alert_both_emotion_and_style(self):
        """Test que verifica que se active alerta combinada cuando ambos factores están presentes."""
        alert, reason = check_combined_alert("frustración", 80.0, "evasivo", 70.0)
        assert alert
        assert "combinada" in reason.lower()
        assert "frustración" in reason.lower()
        assert "evasivo" in reason.lower()
        assert "80" in reason
        assert "70" in reason
        assert "desconexión" in reason.lower() or "riesgo" in reason.lower()
    
    def test_check_combined_alert_case_insensitive(self):
        """Test que verifica que la detección combinada sea case insensitive."""
        alert, reason = check_combined_alert("FRUSTRACIÓN", 80.0, "EVASIVO", 70.0)
        assert alert
        assert "frustración" in reason.lower()
        assert "evasivo" in reason.lower()
        
        alert, reason = check_combined_alert("Tristeza", 75.0, "Pasivo-agresivo", 65.0)
        assert alert
        assert "tristeza" in reason.lower()
        assert "pasivo-agresivo" in reason.lower()
    
    def test_edge_cases_emotion_alert(self):
        """Test casos extremos para alertas emocionales."""
        # Score exacto en el umbral
        alert, reason = check_emotion_alert("frustración", 70.0)
        assert alert
        
        # Score muy alto
        alert, reason = check_emotion_alert("tristeza", 100.0)
        assert alert
        
        # Score cero
        alert, reason = check_emotion_alert("frustración", 0.0)
        assert not alert
        
        # Emoción vacía
        alert, reason = check_emotion_alert("", 80.0)
        assert not alert
    
    def test_edge_cases_style_alert(self):
        """Test casos extremos para alertas de estilo."""
        # Score exacto en el umbral
        assert is_style_alert("evasivo", 60.0)
        
        # Score muy alto
        assert is_style_alert("pasivo-agresivo", 100.0)
        
        # Score cero
        assert not is_style_alert("evasivo", 0.0)
        
        # Estilo vacío
        assert not is_style_alert("", 80.0)
    
    def test_all_emotion_thresholds(self):
        """Test que verifica todos los umbrales de emociones definidos."""
        for emotion, threshold in EMOTION_THRESHOLDS.items():
            # Por debajo del umbral
            assert not is_emotion_alert(emotion, threshold - 1)
            
            # En el umbral
            assert is_emotion_alert(emotion, threshold)
            
            # Por encima del umbral
            assert is_emotion_alert(emotion, threshold + 1)
    
    def test_all_style_risky(self):
        """Test que verifica todos los estilos riesgosos definidos."""
        for style in STYLE_RISKY:
            # Por debajo del umbral (60)
            assert not is_style_alert(style, 59.0)
            
            # En el umbral
            assert is_style_alert(style, 60.0)
            
            # Por encima del umbral
            assert is_style_alert(style, 80.0)
    
    def test_alert_reason_formatting(self):
        """Test que verifica el formato de los mensajes de razón de alerta."""
        # Alerta por emoción
        alert, reason = check_emotion_alert("frustración", 85.0)
        assert alert
        assert "frustración" in reason
        assert "85" in reason
        assert reason.endswith(".")
        
        # Alerta por estilo
        alert, reason = check_combined_alert("alegría", 50.0, "evasivo", 75.0)
        assert alert
        assert "evasivo" in reason
        assert "75" in reason
        assert reason.endswith(".")
        
        # Alerta combinada
        alert, reason = check_combined_alert("tristeza", 80.0, "pasivo-agresivo", 70.0)
        assert alert
        assert "combinada" in reason
        assert "tristeza" in reason
        assert "pasivo-agresivo" in reason
        assert reason.endswith(".") 