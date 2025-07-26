# backend/ml_models/style_classification/utils.py

import re
import unicodedata

def limpiar_texto(texto: str) -> str:
    """
    Normaliza el texto eliminando signos, tildes y lo pasa a minúsculas.
    """
    if not isinstance(texto, str):
        return ""
    
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = texto.lower()
    return texto
