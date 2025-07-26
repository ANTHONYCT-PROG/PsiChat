#!/usr/bin/env python3
"""
Script de inicialización del proyecto PsiChat Backend.
Este script configura automáticamente el entorno de desarrollo.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json


def run_command(command, description):
    """Ejecuta un comando y maneja errores."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error: {e.stderr}")
        return False


def create_directories():
    """Crea los directorios necesarios."""
    directories = [
        "logs",
        "uploads",
        "temp",
        "ml_models/emotion_detection",
        "ml_models/style_classification",
        "backups",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")


def setup_environment():
    """Configura el archivo de entorno."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("📄 Archivo .env creado desde env.example")
        print("⚠️  Recuerda configurar las variables de entorno en .env")
    elif env_file.exists():
        print("📄 Archivo .env ya existe")
    else:
        print("❌ No se encontró env.example")


def install_dependencies():
    """Instala las dependencias del proyecto."""
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        return False
    
    # Instalar dependencias de desarrollo si es necesario
    if "--dev" in sys.argv:
        run_command("pip install -r requirements-dev.txt", "Instalando dependencias de desarrollo")
    
    return True


def setup_database():
    """Configura la base de datos."""
    print("🗄️  Configurando base de datos...")
    
    # Ejecutar migración
    if not run_command("python migrate_database.py", "Ejecutando migración de base de datos"):
        return False
    
    return True


def setup_ml_models():
    """Configura los modelos de machine learning."""
    print("🤖 Configurando modelos de ML...")
    
    # Verificar si los modelos existen
    emotion_model = Path("ml_models/emotion_detection/emotion_model.joblib")
    style_model = Path("ml_models/style_classification/style_model.joblib")
    
    if not emotion_model.exists():
        print("⚠️  Modelo de emociones no encontrado. Ejecutando entrenamiento...")
        if not run_command("python ml_models/emotion_detection/train.py", "Entrenando modelo de emociones"):
            print("❌ Error entrenando modelo de emociones")
    
    if not style_model.exists():
        print("⚠️  Modelo de estilos no encontrado. Ejecutando entrenamiento...")
        if not run_command("python ml_models/style_classification/train.py", "Entrenando modelo de estilos"):
            print("❌ Error entrenando modelo de estilos")
    
    return True


def run_tests():
    """Ejecuta las pruebas del proyecto."""
    print("🧪 Ejecutando pruebas...")
    
    if not run_command("python -m pytest tests/ -v", "Ejecutando pruebas unitarias"):
        print("⚠️  Algunas pruebas fallaron")
        return False
    
    return True


def setup_git_hooks():
    """Configura git hooks para desarrollo."""
    hooks_dir = Path(".git/hooks")
    if hooks_dir.exists():
        # Crear pre-commit hook
        pre_commit = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/sh
# Pre-commit hook para PsiChat Backend

echo "🔍 Ejecutando linting..."
python -m black . --check
python -m isort . --check-only
python -m flake8 .

echo "🧪 Ejecutando pruebas..."
python -m pytest tests/ -v

echo "✅ Pre-commit completado"
"""
        pre_commit.write_text(pre_commit_content)
        pre_commit.chmod(0o755)
        print("🔗 Git hook pre-commit configurado")


def create_docs():
    """Crea la documentación inicial."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Crear README del backend
    readme_content = """# PsiChat Backend

Backend optimizado para la aplicación PsiChat - Chatbot emocional y análisis de comunicación educativa.

## 🚀 Características

- **API RESTful** con FastAPI
- **Base de datos robusta** con SQLAlchemy
- **Análisis emocional** con machine learning
- **Sistema de notificaciones** en tiempo real
- **Autenticación JWT** segura
- **Logging profesional** estructurado
- **Manejo de errores** robusto
- **Métricas y monitoreo** integrados

## 📋 Requisitos

- Python 3.8+
- SQLite (o PostgreSQL para producción)
- Redis (opcional, para caché)

## 🛠️ Instalación

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `source venv/bin/activate` (Linux/Mac) o `venv\\Scripts\\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Configurar variables de entorno: `cp env.example .env`
6. Ejecutar migración: `python migrate_database.py`
7. Iniciar servidor: `python -m uvicorn app.main:app --reload`

## 🔧 Configuración

Edita el archivo `.env` para configurar:

- Base de datos
- Claves de API
- Configuración de CORS
- Logging
- Notificaciones

## 📚 Documentación

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Métricas: http://localhost:8000/metrics (solo en desarrollo)

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
python -m pytest

# Ejecutar con cobertura
python -m pytest --cov=app

# Ejecutar pruebas específicas
python -m pytest tests/test_auth.py
```

## 🚀 Despliegue

### Desarrollo
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 Monitoreo

- **Logs**: `logs/` directory
- **Métricas**: Endpoint `/metrics`
- **Health Check**: Endpoint `/health`

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
"""
    
    readme_file = Path("README.md")
    if not readme_file.exists():
        readme_file.write_text(readme_content)
        print("📄 README.md creado")
    
    # Crear documentación de API
    api_docs = docs_dir / "api.md"
    api_docs_content = """# Documentación de la API

## Endpoints Principales

### Autenticación
- `POST /auth/register` - Registro de usuario
- `POST /auth/login` - Inicio de sesión
- `GET /auth/me` - Perfil del usuario actual

### Chat
- `POST /chat/send` - Enviar mensaje
- `GET /chat/history` - Historial de chat
- `GET /chat/direct/{user_id}` - Chat directo

### Análisis
- `POST /analysis/analyze` - Analizar texto
- `GET /analysis/last` - Último análisis
- `GET /analysis/history` - Historial de análisis

### Tutor
- `GET /tutor/alerts` - Alertas para tutores
- `POST /tutor/intervene` - Intervención de tutor
- `GET /tutor/students` - Lista de estudiantes

## Códigos de Error

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Autenticación

La API usa JWT tokens. Incluye el token en el header:
```
Authorization: Bearer <token>
```
"""
    
    if not api_docs.exists():
        api_docs.write_text(api_docs_content)
        print("📄 Documentación de API creada")


def main():
    """Función principal de inicialización."""
    print("🚀 Iniciando configuración de PsiChat Backend...")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detectado")
    
    # Crear directorios
    create_directories()
    
    # Configurar entorno
    setup_environment()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error instalando dependencias")
        sys.exit(1)
    
    # Configurar base de datos
    if not setup_database():
        print("❌ Error configurando base de datos")
        sys.exit(1)
    
    # Configurar modelos ML
    setup_ml_models()
    
    # Configurar git hooks
    setup_git_hooks()
    
    # Crear documentación
    create_docs()
    
    # Ejecutar pruebas si se solicita
    if "--test" in sys.argv:
        run_tests()
    
    print("=" * 50)
    print("🎉 ¡Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Configura las variables de entorno en .env")
    print("2. Ejecuta: python -m uvicorn app.main:app --reload")
    print("3. Visita: http://localhost:8000/docs")
    print("\n📚 Documentación disponible en docs/")
    print("🧪 Para ejecutar pruebas: python -m pytest")


if __name__ == "__main__":
    main() 