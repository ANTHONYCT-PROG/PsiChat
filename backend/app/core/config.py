"""
Configuración central de PsiChat Backend.
Lee variables de entorno desde `.env` usando `python-dotenv`.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from pathlib import Path
from dotenv import load_dotenv

# Cargar el archivo .env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic para validación."""
    
    # Configuración de la aplicación
    APP_NAME: str = "PsiChat Backend"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Configuración de base de datos
    DATABASE_URL: str = "sqlite:///./psichat.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configuración de CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Configuración de modelos ML
    EMOTION_MODEL_PATH: str = "ml_models/emotion_detection/emotion_model.joblib"
    STYLE_MODEL_PATH: str = "ml_models/style_classification/style_model.joblib"

    # Configuración de servicios externos
    OPENROUTER_API_KEY: str = ""
    MODEL_ID: str = "mistralai/mistral-small-3.2-24b-instruct:free"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Configuración de rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Configuración de caché
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutos
    REDIS_URL: str = ""
    
    # Configuración de notificaciones
    NOTIFICATIONS_ENABLED: bool = True
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Configuración de análisis
    ANALYSIS_BATCH_SIZE: int = 10
    ANALYSIS_TIMEOUT: int = 30
    ENABLE_DEEP_ANALYSIS: bool = True
    
    # Configuración de monitoreo
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY debe ser cambiada en producción")
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL no puede estar vacía")
        return v
    
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

# Configuración específica por entorno
if settings.ENVIRONMENT == "development":
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    # Agregar orígenes adicionales para desarrollo
    additional_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8081",
        "http://127.0.0.1:8081"
    ]
    for origin in additional_origins:
        if origin not in settings.ALLOWED_ORIGINS:
            settings.ALLOWED_ORIGINS.append(origin)

elif settings.ENVIRONMENT == "testing":
    settings.DEBUG = True
    settings.DATABASE_URL = "sqlite:///./test.db"
    settings.LOG_LEVEL = "WARNING"
    settings.CACHE_ENABLED = False
    settings.NOTIFICATIONS_ENABLED = False

# Crear directorios necesarios
def create_directories():
    """Crea los directorios necesarios para la aplicación."""
    directories = [
        Path("logs"),
        Path("ml_models/emotion_detection"),
        Path("ml_models/style_classification"),
        Path("uploads"),
        Path("temp")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Crear directorios al importar el módulo
create_directories()
