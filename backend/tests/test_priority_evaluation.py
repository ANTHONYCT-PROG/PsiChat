# Archivo: test_priority_evaluation.py
"""
Tests para validar la función mejorada de evaluación de prioridad.
"""

import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.analysis_service import evaluate_priority


class TestPriorityEvaluation:
    """Tests para la función de evaluación de prioridad mejorada."""
    
    def test_critical_priority_extreme_emotions(self):
        """Test que verifica prioridad crítica para emociones extremas."""
        # Frustración extrema (90+)
        assert evaluate_priority("frustración", 95.0, "asertivo", 50.0) == "crítica"
        
        # Tristeza profunda (95+)
        assert evaluate_priority("tristeza", 98.0, "empático", 60.0) == "crítica"
        
        # Ansiedad severa (85+)
        assert evaluate_priority("ansiedad", 90.0, "formal", 40.0) == "crítica"
        
        # Desánimo profundo (90+)
        assert evaluate_priority("desánimo", 92.0, "evasivo", 70.0) == "crítica"
    
    def test_high_priority_emotions(self):
        """Test que verifica prioridad alta para emociones de alto riesgo."""
        # Frustración alta (75+)
        assert evaluate_priority("frustración", 80.0, "asertivo", 50.0) == "alta"
        
        # Tristeza alta (80+)
        assert evaluate_priority("tristeza", 85.0, "empático", 60.0) == "alta"
        
        # Ansiedad alta (70+)
        assert evaluate_priority("ansiedad", 75.0, "formal", 40.0) == "alta"
        
        # Desánimo alto (75+)
        assert evaluate_priority("desánimo", 80.0, "evasivo", 70.0) == "alta"
    
    def test_medium_priority_emotions(self):
        """Test que verifica prioridad media para emociones de riesgo medio."""
        # Preocupación (65+)
        assert evaluate_priority("preocupación", 70.0, "asertivo", 50.0) == "media"
        
        # Confusión (60+)
        assert evaluate_priority("confusión", 65.0, "empático", 60.0) == "media"
        
        # Inseguridad (70+)
        assert evaluate_priority("inseguridad", 75.0, "formal", 40.0) == "media"
        
        # Nostalgia (75+)
        assert evaluate_priority("nostalgia", 80.0, "evasivo", 70.0) == "media"
    
    def test_high_priority_styles(self):
        """Test que verifica prioridad alta para estilos de alto riesgo."""
        # Estilo evasivo alto (65+)
        assert evaluate_priority("alegría", 50.0, "evasivo", 70.0) == "alta"
        
        # Estilo pasivo-agresivo alto (60+)
        assert evaluate_priority("tranquilidad", 40.0, "pasivo-agresivo", 65.0) == "alta"
        
        # Estilo agresivo alto (55+)
        assert evaluate_priority("sorpresa", 30.0, "agresivo", 60.0) == "alta"
        
        # Estilo defensivo alto (70+)
        assert evaluate_priority("curiosidad", 45.0, "defensivo", 75.0) == "alta"
    
    def test_medium_priority_styles(self):
        """Test que verifica prioridad media para estilos de riesgo medio."""
        # Estilo formal alto (80+)
        assert evaluate_priority("alegría", 50.0, "formal", 85.0) == "media"
        
        # Estilo distante alto (70+)
        assert evaluate_priority("tranquilidad", 40.0, "distante", 75.0) == "media"
        
        # Estilo sarcástico alto (65+)
        assert evaluate_priority("sorpresa", 30.0, "sarcástico", 70.0) == "media"
    
    def test_combined_risk_factors(self):
        """Test que verifica prioridad cuando se combinan múltiples factores de riesgo."""
        # Emoción alta + estilo alto = crítica
        assert evaluate_priority("frustración", 80.0, "evasivo", 70.0) == "crítica"
        
        # Emoción media + estilo alto = alta
        assert evaluate_priority("preocupación", 70.0, "agresivo", 60.0) == "alta"
        
        # Emoción alta + estilo medio = alta
        assert evaluate_priority("tristeza", 85.0, "formal", 85.0) == "alta"
        
        # Emoción media + estilo medio = media
        assert evaluate_priority("confusión", 65.0, "distante", 75.0) == "media"
    
    def test_context_risk_adjustment(self):
        """Test que verifica el ajuste por contexto de riesgo."""
        # Sin contexto de riesgo
        assert evaluate_priority("frustración", 75.0, "asertivo", 50.0) == "alta"
        
        # Con contexto de riesgo alto
        assert evaluate_priority("frustración", 75.0, "asertivo", 50.0, "alto") == "crítica"
        
        # Con contexto de riesgo medio
        assert evaluate_priority("preocupación", 65.0, "asertivo", 50.0, "medio") == "media"
        
        # Con contexto de riesgo normal
        assert evaluate_priority("alegría", 50.0, "asertivo", 50.0, "normal") == "normal"
    
    def test_low_priority_cases(self):
        """Test que verifica prioridad baja para casos de riesgo mínimo."""
        # Emoción de riesgo medio con score bajo
        assert evaluate_priority("preocupación", 60.0, "asertivo", 50.0) == "baja"
        
        # Estilo de riesgo medio con score bajo
        assert evaluate_priority("alegría", 50.0, "formal", 70.0) == "baja"
        
        # Emoción de alto riesgo con score muy bajo
        assert evaluate_priority("frustración", 65.0, "asertivo", 50.0) == "baja"
    
    def test_normal_priority_cases(self):
        """Test que verifica prioridad normal para casos sin riesgo."""
        # Emociones positivas
        assert evaluate_priority("alegría", 80.0, "asertivo", 70.0) == "normal"
        assert evaluate_priority("tranquilidad", 75.0, "empático", 80.0) == "normal"
        assert evaluate_priority("sorpresa", 60.0, "formal", 65.0) == "normal"
        
        # Emociones neutras
        assert evaluate_priority("curiosidad", 70.0, "asertivo", 60.0) == "normal"
        assert evaluate_priority("interés", 65.0, "empático", 75.0) == "normal"
    
    def test_case_insensitive_emotions(self):
        """Test que verifica que la evaluación sea case insensitive para emociones."""
        assert evaluate_priority("FRUSTRACIÓN", 80.0, "asertivo", 50.0) == "alta"
        assert evaluate_priority("Tristeza", 85.0, "empático", 60.0) == "alta"
        assert evaluate_priority("Ansiedad", 75.0, "formal", 40.0) == "alta"
        assert evaluate_priority("DESÁNIMO", 80.0, "evasivo", 70.0) == "alta"
    
    def test_case_insensitive_styles(self):
        """Test que verifica que la evaluación sea case insensitive para estilos."""
        assert evaluate_priority("alegría", 50.0, "EVASIVO", 70.0) == "alta"
        assert evaluate_priority("tranquilidad", 40.0, "Pasivo-agresivo", 65.0) == "alta"
        assert evaluate_priority("sorpresa", 30.0, "AGRESIVO", 60.0) == "alta"
        assert evaluate_priority("curiosidad", 45.0, "Defensivo", 75.0) == "alta"
    
    def test_edge_cases(self):
        """Test casos extremos y límites."""
        # Scores exactos en umbrales
        assert evaluate_priority("frustración", 75.0, "asertivo", 50.0) == "alta"
        assert evaluate_priority("tristeza", 80.0, "empático", 60.0) == "alta"
        assert evaluate_priority("ansiedad", 70.0, "formal", 40.0) == "alta"
        
        # Scores justo por debajo de umbrales
        assert evaluate_priority("frustración", 74.9, "asertivo", 50.0) == "baja"
        assert evaluate_priority("tristeza", 79.9, "empático", 60.0) == "baja"
        assert evaluate_priority("ansiedad", 69.9, "formal", 40.0) == "baja"
        
        # Scores muy altos
        assert evaluate_priority("frustración", 100.0, "asertivo", 50.0) == "crítica"
        assert evaluate_priority("tristeza", 100.0, "empático", 60.0) == "crítica"
        
        # Scores muy bajos
        assert evaluate_priority("frustración", 0.0, "asertivo", 50.0) == "normal"
        assert evaluate_priority("tristeza", 10.0, "empático", 60.0) == "normal"
    
    def test_unknown_emotions_and_styles(self):
        """Test que verifica comportamiento con emociones y estilos no definidos."""
        # Emociones desconocidas
        assert evaluate_priority("euforia", 90.0, "asertivo", 50.0) == "normal"
        assert evaluate_priority("melancolía", 85.0, "empático", 60.0) == "normal"
        
        # Estilos desconocidos
        assert evaluate_priority("alegría", 50.0, "colaborativo", 80.0) == "normal"
        assert evaluate_priority("tranquilidad", 40.0, "dinámico", 75.0) == "normal"
        
        # Ambos desconocidos
        assert evaluate_priority("euforia", 90.0, "colaborativo", 80.0) == "normal"
    
    def test_priority_levels_completeness(self):
        """Test que verifica que todos los niveles de prioridad sean alcanzables."""
        priorities = set()
        
        # Probar diferentes combinaciones para obtener todos los niveles
        test_cases = [
            ("frustración", 95.0, "evasivo", 80.0),  # crítica
            ("frustración", 80.0, "asertivo", 50.0),  # alta
            ("preocupación", 70.0, "asertivo", 50.0),  # media
            ("preocupación", 60.0, "asertivo", 50.0),  # baja
            ("alegría", 80.0, "asertivo", 70.0),      # normal
        ]
        
        for emotion, emotion_score, style, style_score in test_cases:
            priority = evaluate_priority(emotion, emotion_score, style, style_score)
            priorities.add(priority)
        
        # Verificar que se obtengan todos los niveles
        expected_priorities = {"crítica", "alta", "media", "baja", "normal"}
        assert priorities == expected_priorities 