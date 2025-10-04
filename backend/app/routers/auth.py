"""
Router para autenticación y manejo de sesiones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas
from app.utils import security

router = APIRouter()

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# =============================================
# DEPENDENCIAS
# =============================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """
    Obtiene el usuario actual desde el token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar token
    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    id_usuario: int = payload.get("id_usuario")
    
    if username is None or id_usuario is None:
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario,
        models.Usuario.NombreUsuario == username
    ).first()
    
    if usuario is None:
        raise credentials_exception
    
    if not usuario.Activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    if usuario.Bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario bloqueado por múltiples intentos fallidos"
        )
    
    return usuario


def get_current_active_user(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """
    Verifica que el usuario esté activo
    """
    if not current_user.Activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


# =============================================
# ENDPOINTS DE AUTENTICACIÓN
# =============================================

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Inicio de sesión - Genera token JWT
    """
    # Buscar usuario
    usuario = db.query(models.Usuario).filter(
        models.Usuario.NombreUsuario == form_data.username
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si está bloqueado
    if usuario.Bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario bloqueado por múltiples intentos fallidos. Contacte al administrador."
        )
    
    # Verificar contraseña
    if not security.verify_password(form_data.password, usuario.ContrasenaHash):
        # Incrementar intentos fallidos
        usuario.IntentosLogin += 1
        
        # Bloquear si excede los intentos permitidos (3 por defecto)
        if usuario.IntentosLogin >= 3:
            usuario.Bloqueado = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta bloqueada por múltiples intentos fallidos"
            )
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Usuario o contraseña incorrectos. Intento {usuario.IntentosLogin} de 3",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si está activo
    if not usuario.Activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Login exitoso - resetear intentos y actualizar último acceso
    usuario.IntentosLogin = 0
    usuario.UltimoAcceso = datetime.utcnow()
    db.commit()
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={
            "sub": usuario.NombreUsuario,
            "id_usuario": usuario.IdUsuario,
            "rol": usuario.IdRol
        },
        expires_delta=access_token_expires
    )
    
    # Registrar en auditoría
    auditoria = models.AuditoriaAccesos(
        IdUsuario=usuario.IdUsuario,
        Accion="LOGIN",
        Exitoso=True
    )
    db.add(auditoria)
    db.commit()
    
    # Preparar respuesta con datos del usuario
    usuario_out = schemas.UsuarioOut.from_orm(usuario)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario_out
    }


@router.post("/login-json", response_model=schemas.Token)
def login_json(
    login_data: schemas.Login,
    db: Session = Depends(get_db)
):
    """
    Inicio de sesión alternativo con JSON (para frontend Vue)
    """
    # Buscar usuario
    usuario = db.query(models.Usuario).filter(
        models.Usuario.NombreUsuario == login_data.nombre_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    # Verificar si está bloqueado
    if usuario.Bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario bloqueado. Contacte al administrador."
        )
    
    # Verificar contraseña
    if not security.verify_password(login_data.contrasena, usuario.ContrasenaHash):
        usuario.IntentosLogin += 1
        
        if usuario.IntentosLogin >= 3:
            usuario.Bloqueado = True
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credenciales incorrectas. Intento {usuario.IntentosLogin} de 3"
        )
    
    if not usuario.Activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Login exitoso
    usuario.IntentosLogin = 0
    usuario.UltimoAcceso = datetime.utcnow()
    db.commit()
    
    # Crear token
    access_token = security.create_access_token(
        data={
            "sub": usuario.NombreUsuario,
            "id_usuario": usuario.IdUsuario,
            "rol": usuario.IdRol
        }
    )
    
    # Auditoría
    auditoria = models.AuditoriaAccesos(
        IdUsuario=usuario.IdUsuario,
        Accion="LOGIN",
        Exitoso=True
    )
    db.add(auditoria)
    db.commit()
    
    usuario_out = schemas.UsuarioOut.from_orm(usuario)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario_out
    }


@router.post("/logout")
def logout(
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cerrar sesión (registrar en auditoría)
    """
    auditoria = models.AuditoriaAccesos(
        IdUsuario=current_user.IdUsuario,
        Accion="LOGOUT",
        Exitoso=True
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Sesión cerrada correctamente"}


@router.get("/me", response_model=schemas.UsuarioOut)
def obtener_usuario_actual(
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual
    """
    return current_user


@router.post("/cambiar-contrasena")
def cambiar_contrasena(
    datos: schemas.CambiarContrasena,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario actual
    """
    # Verificar contraseña actual
    if not security.verify_password(datos.contrasena_actual, current_user.ContrasenaHash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar nueva contraseña
    es_valida, mensaje = security.validate_password_strength(datos.contrasena_nueva)
    if not es_valida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensaje
        )
    
    # Actualizar contraseña
    current_user.ContrasenaHash = security.hash_password(datos.contrasena_nueva)
    db.commit()
    
    # Registrar en auditoría
    auditoria = models.AuditoriaAccesos(
        IdUsuario=current_user.IdUsuario,
        Accion="CAMBIO_CONTRASENA",
        Exitoso=True
    )
    db.add(auditoria)
    db.commit()
    
    return {"mensaje": "Contraseña cambiada correctamente"}


@router.post("/desbloquear-usuario/{id_usuario}")
def desbloquear_usuario(
    id_usuario: int,
    current_user: models.Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Desbloquear un usuario (solo administradores)
    """
    # Verificar que el usuario actual sea administrador
    if current_user.IdRol != 1:  # 1 = Administrador
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción"
        )
    
    # Buscar usuario a desbloquear
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Desbloquear
    usuario.Bloqueado = False
    usuario.IntentosLogin = 0
    db.commit()
    
    return {"mensaje": f"Usuario {usuario.NombreUsuario} desbloqueado correctamente"}