"""
Router para operaciones CRUD de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.utils import security
from app.routers.auth import get_current_active_user

router = APIRouter()

# =============================================
# ENDPOINTS DE USUARIOS
# =============================================

@router.get("/", response_model=List[schemas.UsuarioOut])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = None,
    rol: Optional[int] = None,
    buscar: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Listar todos los usuarios (solo administradores)
    """
    # Verificar que sea administrador
    if current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    query = db.query(models.Usuario)
    
    # Aplicar filtros
    if activo is not None:
        query = query.filter(models.Usuario.Activo == activo)
    
    if rol:
        query = query.filter(models.Usuario.IdRol == rol)
    
    if buscar:
        query = query.filter(
            (models.Usuario.NombreUsuario.like(f"%{buscar}%")) |
            (models.Usuario.NombreCompleto.like(f"%{buscar}%")) |
            (models.Usuario.Email.like(f"%{buscar}%"))
        )
    
    usuarios = query.offset(skip).limit(limit).all()
    return usuarios


@router.get("/{id_usuario}", response_model=schemas.UsuarioOut)
def obtener_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener un usuario específico
    """
    # Solo puede ver su propio perfil o ser admin
    if current_user.IdUsuario != id_usuario and current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return usuario


@router.post("/", response_model=schemas.UsuarioOut, status_code=201)
def crear_usuario(
    usuario: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo usuario (solo administradores)
    """
    # Verificar permisos
    if current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    # Verificar si el nombre de usuario ya existe
    existe = db.query(models.Usuario).filter(
        models.Usuario.NombreUsuario == usuario.NombreUsuario
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya existe"
        )
    
    # Validar email si se proporciona
    if usuario.Email:
        email_existe = db.query(models.Usuario).filter(
            models.Usuario.Email == usuario.Email
        ).first()
        if email_existe:
            raise HTTPException(
                status_code=400,
                detail="El email ya está registrado"
            )
    
    # Validar contraseña
    es_valida, mensaje = security.validate_password_strength(usuario.Contrasena)
    if not es_valida:
        raise HTTPException(status_code=400, detail=mensaje)
    
    # Crear usuario
    nuevo_usuario = models.Usuario(
        NombreUsuario=usuario.NombreUsuario,
        ContrasenaHash=security.hash_password(usuario.Contrasena),
        NombreCompleto=usuario.NombreCompleto,
        Email=usuario.Email,
        IdRol=usuario.IdRol,
        Activo=True,
        Bloqueado=False
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


@router.put("/{id_usuario}", response_model=schemas.UsuarioOut)
def actualizar_usuario(
    id_usuario: int,
    usuario_update: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un usuario existente
    """
    # Verificar permisos: puede actualizar su propio perfil o ser admin
    if current_user.IdUsuario != id_usuario and current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    # Buscar usuario
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar campos
    update_data = usuario_update.dict(exclude_unset=True)
    
    # Verificar email único si se actualiza
    if 'Email' in update_data and update_data['Email']:
        email_existe = db.query(models.Usuario).filter(
            models.Usuario.Email == update_data['Email'],
            models.Usuario.IdUsuario != id_usuario
        ).first()
        if email_existe:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
    
    # Solo admin puede cambiar rol y estado activo
    if current_user.IdRol != 1:
        update_data.pop('IdRol', None)
        update_data.pop('Activo', None)
    
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


@router.delete("/{id_usuario}")
def eliminar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Eliminar (desactivar) un usuario (solo administradores)
    """
    # Solo admin puede eliminar usuarios
    if current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    # No puede eliminarse a sí mismo
    if current_user.IdUsuario == id_usuario:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminar tu propio usuario"
        )
    
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Soft delete
    usuario.Activo = False
    db.commit()
    
    return {"mensaje": "Usuario eliminado correctamente"}


@router.post("/{id_usuario}/activar")
def activar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Activar un usuario desactivado (solo administradores)
    """
    if current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.Activo = True
    db.commit()
    
    return {"mensaje": "Usuario activado correctamente"}


@router.post("/{id_usuario}/resetear-password")
def resetear_password(
    id_usuario: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Resetear contraseña de un usuario (genera password temporal)
    """
    if current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    usuario = db.query(models.Usuario).filter(
        models.Usuario.IdUsuario == id_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Generar contraseña temporal
    temp_password = security.generate_temp_password()
    
    # Actualizar contraseña
    usuario.ContrasenaHash = security.hash_password(temp_password)
    usuario.Bloqueado = False
    usuario.IntentosLogin = 0
    
    db.commit()
    
    return {
        "mensaje": "Contraseña reseteada correctamente",
        "password_temporal": temp_password,
        "nota": "El usuario debe cambiar esta contraseña al iniciar sesión"
    }


@router.get("/rol/{id_rol}", response_model=List[schemas.UsuarioOut])
def listar_usuarios_por_rol(
    id_rol: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Listar usuarios por rol
    """
    if current_user.IdRol != 1:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    usuarios = db.query(models.Usuario).filter(
        models.Usuario.IdRol == id_rol,
        models.Usuario.Activo == True
    ).all()
    
    return usuarios