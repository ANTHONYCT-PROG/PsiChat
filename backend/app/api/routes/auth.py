# backend/app/api/routes/auth.py
"""
Rutas para autenticación y registro de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserLogin, UserOut, UserLoginResponse
from app.core import security
from app.db import crud
from app.db.models import RolUsuario
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from app.db import models

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Dependencia de base de datos ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





# ---------- Registro de usuario ----------
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    
    # Si no se especifica rol, determinarlo por email
    if not user.rol:
        user.rol = crud.determinar_rol_por_email(db, user.email)
    
    new_user = crud.create_user(db, user)
    return new_user


# ---------- Login y generación de token ----------
@router.post("/login", response_model=UserLoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not security.verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    
    token = security.create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user": user
    }


# ---------- Obtener usuario autenticado ----------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = security.decode_access_token(token)
        if not payload or "sub" not in payload:
            raise credentials_exception
        user_id = int(payload["sub"])
    except (JWTError, ValueError):
        raise credentials_exception

    user = crud.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    return user


# ---------- Obtener perfil del usuario actual ----------
@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user = Depends(get_current_user)):
    return current_user


# ---------- Obtener usuarios por rol (solo para tutores) ----------
@router.get("/users/{rol}", response_model=list[UserOut])
def get_users_by_role(
    rol: RolUsuario, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Solo los tutores pueden ver listas de usuarios
    if current_user.rol != RolUsuario.TUTOR:
        raise HTTPException(
            status_code=403, 
            detail="Solo los tutores pueden acceder a esta información."
        )
    
    users = crud.get_users_by_role(db, rol=rol)
    return users


# ---------- Obtener todos los estudiantes (solo para tutores) ----------
@router.get("/students", response_model=list[UserOut])
def get_all_students(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Solo los tutores pueden ver la lista de estudiantes
    if current_user.rol != RolUsuario.TUTOR:
        raise HTTPException(
            status_code=403, 
            detail="Solo los tutores pueden acceder a esta información."
        )
    
    students = crud.get_users_by_role(db, rol=RolUsuario.ESTUDIANTE)
    return students
