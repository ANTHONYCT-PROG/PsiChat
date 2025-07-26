# Archivo: dependencies.py
"""
Dependencias compartidas para FastAPI.
"""

from app.api.routes.auth import get_current_user

__all__ = ["get_current_user"]
