"""
Archivo principal de arranque para la API de PsiChat.
Incluye configuración de CORS, middleware, manejo de errores y logging.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import auth, chat, analysis, tutor
from app.core.config import settings
from app.core.logging import logger, performance_logger
from app.core.exceptions import PsiChatException, handle_psichat_exception, handle_generic_exception


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    # Startup
    logger.info("Iniciando PsiChat Backend...")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Base de datos: {settings.DATABASE_URL}")
    
    # Crear métricas de inicio
    # try:
    #     from app.db.session import SessionLocal
    #     from app.db import crud
        
    #     db = SessionLocal()
    #     crud.create_metric(
    #         db, 
    #         "sistema", 
    #         "aplicacion_iniciada", 
    #         1.0, 
    #         "evento",
    #         {"timestamp": time.time()}
    #     )
    #     db.close()
    # except Exception as e:
    #     logger.error("Error creando métrica de inicio", error=e)
    
    yield
    
    # Shutdown
    logger.info("Cerrando PsiChat Backend...")


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API de análisis emocional, estilo comunicativo y chatbot educativo con empatía.",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Middleware de hosts confiables
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configurar hosts específicos en producción
    )

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para loggear todas las requests."""
    start_time = time.time()
    
    # Log de la request
    logger.api(f"Request iniciada", {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    })
    
    try:
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        process_time = time.time() - start_time
        
        # Log de la respuesta
        logger.api(f"Request completada", {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": round(process_time * 1000, 2)
        })
        
        # Crear métrica de rendimiento
        performance_logger.log_request_time(
            str(request.url.path),
            request.method,
            process_time,
            response.status_code
        )
        
        # Agregar header de tiempo de respuesta
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log de error
        process_time = time.time() - start_time
        logger.error(f"Request falló", error=e, data={
            "method": request.method,
            "url": str(request.url),
            "duration_ms": round(process_time * 1000, 2)
        })
        raise


# Middleware para manejo de errores
@app.exception_handler(PsiChatException)
async def psichat_exception_handler(request: Request, exc: PsiChatException):
    """Maneja excepciones personalizadas de PsiChat."""
    logger.error(f"Excepción PsiChat capturada", error=exc, data={
        "method": request.method,
        "url": str(request.url),
        "error_code": exc.error_code
    })
    
    http_exception = handle_psichat_exception(exc)
    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Maneja excepciones HTTP de Starlette."""
    logger.error(f"Excepción HTTP capturada", error=exc, data={
        "method": request.method,
        "url": str(request.url),
        "status_code": exc.status_code
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "details": {"status_code": exc.status_code}
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de requests."""
    logger.error(f"Error de validación capturado", error=exc, data={
        "method": request.method,
        "url": str(request.url),
        "errors": exc.errors()
    })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Error de validación en los datos de entrada",
            "details": {
                "errors": exc.errors(),
                "body": exc.body
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones genéricas no capturadas."""
    logger.critical(f"Excepción no manejada capturada", error=exc, data={
        "method": request.method,
        "url": str(request.url),
        "exception_type": type(exc).__name__
    })
    
    http_exception = handle_generic_exception(exc)
    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail
    )


# Incluir rutas principales
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(analysis.router, prefix="/analysis", tags=["Análisis"])
app.include_router(tutor.router, prefix="/tutor", tags=["Tutor"])


# Ruta raíz
@app.get("/")
async def root():
    """Ruta raíz de la API."""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }


# Ruta de health check
@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo."""
    try:
        # Verificar conexión a base de datos
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error("Health check falló", error=e)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "database": "disconnected",
                "error": str(e)
            }
        )


# Ruta de información del sistema
@app.get("/info")
async def system_info():
    """Información del sistema para debugging."""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_url": settings.DATABASE_URL.split("://")[0] + "://***",  # Ocultar detalles sensibles
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "features": {
            "analysis_enabled": True,
            "chat_enabled": True,
            "notifications_enabled": settings.NOTIFICATIONS_ENABLED,
            "cache_enabled": settings.CACHE_ENABLED,
            "metrics_enabled": settings.ENABLE_METRICS
        }
    }


# Ruta de métricas (solo en desarrollo)
@app.get("/metrics")
async def get_metrics():
    """Endpoint para obtener métricas del sistema."""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        from app.db.session import SessionLocal
        from app.db.models import Metricas
        
        db = SessionLocal()
        metrics = db.query(Metricas).order_by(Metricas.creado_en.desc()).limit(50).all()
        db.close()
        
        return {
            "metrics": [
                {
                    "id": m.id,
                    "tipo": m.tipo_metrica,
                    "nombre": m.nombre,
                    "valor": m.valor,
                    "unidad": m.unidad,
                    "creado_en": m.creado_en.isoformat()
                }
                for m in metrics
            ]
        }
    except Exception as e:
        logger.error("Error obteniendo métricas", error=e)
        raise HTTPException(status_code=500, detail="Error obteniendo métricas")


def start_uvicorn():
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    start_uvicorn()

