"""
Configuración de pytest para PsiChat Backend
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
import shutil

from app.main import app
from app.db.session import get_db
from app.db.models import Base
from app.core.config import settings
from app.db import crud
from app.schemas.user import UserCreate
from app.db.models import RolUsuario


# Configuración de base de datos de prueba
@pytest.fixture(scope="session")
def test_db():
    """Crear base de datos de prueba en memoria"""
    # Crear directorio temporal para la base de datos
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    # Crear engine de SQLite en memoria para tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión de prueba
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal
    
    # Limpiar después de los tests
    Base.metadata.drop_all(bind=engine)
    shutil.rmtree(temp_dir)


@pytest.fixture
def db_session(test_db):
    """Sesión de base de datos para cada test"""
    session = test_db()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Cliente de prueba de FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# Fixtures de datos de prueba
@pytest.fixture
def test_student_data():
    """Datos de prueba para un estudiante"""
    return {
        "email": "estudiante.test@example.com",
        "nombre": "Estudiante Test",
        "apellido": "Apellido Test",
        "password": "password123",
        "rol": RolUsuario.ESTUDIANTE
    }


@pytest.fixture
def test_tutor_data():
    """Datos de prueba para un tutor"""
    return {
        "email": "tutor.test@example.com",
        "nombre": "Tutor Test",
        "apellido": "Apellido Test",
        "password": "password123",
        "rol": RolUsuario.TUTOR
    }


@pytest.fixture
def test_admin_data():
    """Datos de prueba para un admin"""
    return {
        "email": "admin.test@example.com",
        "nombre": "Admin Test",
        "apellido": "Apellido Test",
        "password": "password123",
        "rol": RolUsuario.ADMIN
    }


@pytest.fixture
def test_student(db_session, test_student_data):
    """Crear un estudiante de prueba en la base de datos"""
    user_create = UserCreate(**test_student_data)
    user = crud.create_user(db_session, user_create)
    return user


@pytest.fixture
def test_tutor(db_session, test_tutor_data):
    """Crear un tutor de prueba en la base de datos"""
    user_create = UserCreate(**test_tutor_data)
    user = crud.create_user(db_session, user_create)
    return user


@pytest.fixture
def test_admin(db_session, test_admin_data):
    """Crear un admin de prueba en la base de datos"""
    user_create = UserCreate(**test_admin_data)
    user = crud.create_user(db_session, user_create)
    return user


@pytest.fixture
def auth_headers_student(client, test_student_data):
    """Headers de autenticación para estudiante"""
    response = client.post("/auth/login", data={
        "username": test_student_data["email"],
        "password": test_student_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_tutor(client, test_tutor_data):
    """Headers de autenticación para tutor"""
    response = client.post("/auth/login", data={
        "username": test_tutor_data["email"],
        "password": test_tutor_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client, test_admin_data):
    """Headers de autenticación para admin"""
    response = client.post("/auth/login", data={
        "username": test_admin_data["email"],
        "password": test_admin_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Configuración de pytest
def pytest_configure(config):
    """Configuración adicional de pytest"""
    # Configurar variables de entorno para tests
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["LOG_LEVEL"] = "ERROR"


def pytest_collection_modifyitems(config, items):
    """Modificar items de colección de tests"""
    # Marcar tests que requieren base de datos
    for item in items:
        if "test_db" in item.fixturenames:
            item.add_marker(pytest.mark.database)
        if "client" in item.fixturenames:
            item.add_marker(pytest.mark.integration)
        if "auth_headers" in item.fixturenames:
            item.add_marker(pytest.mark.auth) 