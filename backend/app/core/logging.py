"""
Sistema de logging profesional para PsiChat Backend.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json
from functools import wraps
import traceback


class PsiChatLogger:
    """Logger personalizado para PsiChat con diferentes niveles y categorías."""
    
    def __init__(self, name: str = "psichat"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los handlers para diferentes niveles de logging."""
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # Handler para archivo de errores
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        error_handler = logging.FileHandler(log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        
        # Handler para archivo de debug
        debug_handler = logging.FileHandler(log_dir / "debug.log")
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        debug_handler.setFormatter(debug_formatter)
        
        # Handler para archivo de acceso
        access_handler = logging.FileHandler(log_dir / "access.log")
        access_handler.setLevel(logging.INFO)
        access_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        access_handler.setFormatter(access_formatter)
        
        # Agregar handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(access_handler)
    
    def debug(self, message: str, data: Optional[dict] = None):
        """Log de debug."""
        if data:
            message = f"{message} | Data: {json.dumps(data, default=str)}"
        self.logger.debug(message)
    
    def info(self, message: str, data: Optional[dict] = None):
        """Log de información."""
        if data:
            message = f"{message} | Data: {json.dumps(data, default=str)}"
        self.logger.info(message)
    
    def warning(self, message: str, data: Optional[dict] = None):
        """Log de advertencia."""
        if data:
            message = f"{message} | Data: {json.dumps(data, default=str)}"
        self.logger.warning(message)
    
    def error(self, message: str, error: Optional[Exception] = None, data: Optional[dict] = None):
        """Log de error."""
        if error:
            message = f"{message} | Error: {str(error)} | Traceback: {traceback.format_exc()}"
        if data:
            message = f"{message} | Data: {json.dumps(data, default=str)}"
        self.logger.error(message)
    
    def critical(self, message: str, error: Optional[Exception] = None, data: Optional[dict] = None):
        """Log crítico."""
        if error:
            message = f"{message} | Error: {str(error)} | Traceback: {traceback.format_exc()}"
        if data:
            message = f"{message} | Data: {json.dumps(data, default=str)}"
        self.logger.critical(message)
    
    # Métodos específicos por categoría
    def auth(self, message: str, data: Optional[dict] = None):
        """Log específico para autenticación."""
        self.info(f"[AUTH] {message}", data)
    
    def api(self, message: str, data: Optional[dict] = None):
        """Log específico para API."""
        self.info(f"[API] {message}", data)
    
    def db(self, message: str, data: Optional[dict] = None):
        """Log específico para base de datos."""
        self.info(f"[DB] {message}", data)
    
    def analysis(self, message: str, data: Optional[dict] = None):
        """Log específico para análisis."""
        self.info(f"[ANALYSIS] {message}", data)
    
    def chat(self, message: str, data: Optional[dict] = None):
        """Log específico para chat."""
        self.info(f"[CHAT] {message}", data)
    
    def security(self, message: str, data: Optional[dict] = None):
        """Log específico para seguridad."""
        self.warning(f"[SECURITY] {message}", data)


# Instancia global del logger
logger = PsiChatLogger()


def log_function_call(func):
    """Decorador para loggear llamadas a funciones."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__}", {
            "args": str(args),
            "kwargs": str(kwargs)
        })
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed", error=e)
            raise
    return wrapper


def log_api_request(func):
    """Decorador para loggear requests de API."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.api(f"API Request: {func.__name__}", {
            "args": str(args),
            "kwargs": str(kwargs)
        })
        try:
            result = await func(*args, **kwargs)
            logger.api(f"API Response: {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"API Error: {func.__name__} failed", error=e)
            raise
    return wrapper


def log_database_operation(func):
    """Decorador para loggear operaciones de base de datos."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.db(f"DB Operation: {func.__name__}", {
            "args": str(args),
            "kwargs": str(kwargs)
        })
        try:
            result = func(*args, **kwargs)
            logger.db(f"DB Operation: {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"DB Error: {func.__name__} failed", error=e)
            raise
    return wrapper


class PerformanceLogger:
    """Logger para métricas de rendimiento."""
    
    def __init__(self):
        self.logger = PsiChatLogger("performance")
    
    def log_request_time(self, endpoint: str, method: str, duration: float, status_code: int):
        """Log del tiempo de respuesta de una request."""
        self.logger.info(f"Request Performance", {
            "endpoint": endpoint,
            "method": method,
            "duration_ms": round(duration * 1000, 2),
            "status_code": status_code
        })
    
    def log_database_query_time(self, query: str, duration: float):
        """Log del tiempo de ejecución de queries."""
        self.logger.db(f"Query Performance", {
            "query": query[:100] + "..." if len(query) > 100 else query,
            "duration_ms": round(duration * 1000, 2)
        })
    
    def log_analysis_time(self, analysis_type: str, duration: float):
        """Log del tiempo de análisis."""
        self.logger.analysis(f"Analysis Performance", {
            "type": analysis_type,
            "duration_ms": round(duration * 1000, 2)
        })


# Instancia global del performance logger
performance_logger = PerformanceLogger() 