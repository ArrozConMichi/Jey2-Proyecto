"""
Funciones CRUD genéricas y reutilizables
Operaciones comunes de base de datos para todos los modelos
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_, func
from typing import Optional, List, Dict, Any, Type, TypeVar
from fastapi import HTTPException
from app.database import Base

# TypeVar para tipado genérico
ModelType = TypeVar("ModelType", bound=Base)

# =============================================
# OPERACIONES BÁSICAS CRUD
# =============================================

def crear_registro(
    db: Session, 
    model: Type[ModelType], 
    obj_data: dict,
    commit: bool = True
) -> ModelType:
    """
    Crear un registro en la base de datos
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo SQLAlchemy
        obj_data: Diccionario con los datos del objeto
        commit: Si se hace commit inmediatamente (útil para transacciones)
        
    Returns:
        Instancia del modelo creada
        
    Raises:
        HTTPException: Si hay error de integridad o creación
    """
    try:
        instancia = model(**obj_data)
        db.add(instancia)
        
        if commit:
            db.commit()
            db.refresh(instancia)
        
        return instancia
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        
        # Detectar errores comunes
        if "UNIQUE" in error_msg or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un registro con esos datos únicos"
            )
        elif "FOREIGN KEY" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="El registro hace referencia a datos que no existen"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Error de integridad: {error_msg}"
            )
            
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear registro: {str(e)}"
        )


def obtener_registro(
    db: Session, 
    model: Type[ModelType], 
    id_field: str, 
    id_val: Any,
    raise_not_found: bool = False
) -> Optional[ModelType]:
    """
    Obtener un registro por su ID
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        id_field: Nombre del campo ID (ej: 'IdProducto')
        id_val: Valor del ID
        raise_not_found: Si lanza excepción cuando no encuentra el registro
        
    Returns:
        Instancia del modelo o None
        
    Raises:
        HTTPException: Si raise_not_found=True y no se encuentra
    """
    try:
        registro = db.query(model).filter(
            getattr(model, id_field) == id_val
        ).first()
        
        if not registro and raise_not_found:
            raise HTTPException(
                status_code=404,
                detail=f"{model.__tablename__} no encontrado"
            )
        
        return registro
        
    except AttributeError:
        raise HTTPException(
            status_code=500,
            detail=f"Campo '{id_field}' no existe en {model.__tablename__}"
        )


def obtener_por_campo(
    db: Session,
    model: Type[ModelType],
    campo: str,
    valor: Any,
    raise_not_found: bool = False
) -> Optional[ModelType]:
    """
    Obtener un registro por cualquier campo único
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        campo: Nombre del campo (ej: 'CodigoBarras', 'Email')
        valor: Valor a buscar
        raise_not_found: Si lanza excepción cuando no encuentra
        
    Returns:
        Instancia del modelo o None
    """
    try:
        registro = db.query(model).filter(
            getattr(model, campo) == valor
        ).first()
        
        if not registro and raise_not_found:
            raise HTTPException(
                status_code=404,
                detail=f"{model.__tablename__} con {campo}={valor} no encontrado"
            )
        
        return registro
        
    except AttributeError:
        raise HTTPException(
            status_code=500,
            detail=f"Campo '{campo}' no existe en {model.__tablename__}"
        )


def listar_registros(
    db: Session, 
    model: Type[ModelType], 
    skip: int = 0, 
    limit: int = 100, 
    filtros: Optional[Dict[str, Any]] = None,
    ordenar_por: Optional[str] = None,
    orden_desc: bool = False,
    buscar: Optional[Dict[str, str]] = None
) -> List[ModelType]:
    """
    Listar registros con filtros, búsqueda y paginación
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        skip: Número de registros a saltar (paginación)
        limit: Máximo de registros a retornar
        filtros: Diccionario de filtros exactos {campo: valor}
        ordenar_por: Campo por el cual ordenar
        orden_desc: Si el orden es descendente
        buscar: Diccionario para búsqueda con LIKE {campo: texto}
        
    Returns:
        Lista de instancias del modelo
        
    Example:
        # Buscar productos activos con nombre que contenga "arroz"
        productos = listar_registros(
            db, Producto,
            filtros={"Activo": True},
            buscar={"NombreProducto": "arroz"}
        )
    """
    try:
        query = db.query(model)
        
        # Aplicar filtros exactos
        if filtros:
            for field, val in filtros.items():
                if hasattr(model, field):
                    query = query.filter(getattr(model, field) == val)
        
        # Aplicar búsqueda con LIKE
        if buscar:
            condiciones = []
            for field, texto in buscar.items():
                if hasattr(model, field):
                    condiciones.append(
                        getattr(model, field).like(f"%{texto}%")
                    )
            if condiciones:
                query = query.filter(or_(*condiciones))
        
        # Aplicar ordenamiento
        if ordenar_por and hasattr(model, ordenar_por):
            campo_orden = getattr(model, ordenar_por)
            if orden_desc:
                query = query.order_by(campo_orden.desc())
            else:
                query = query.order_by(campo_orden)
        
        # Aplicar paginación
        return query.offset(skip).limit(limit).all()
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar registros: {str(e)}"
        )


def contar_registros(
    db: Session,
    model: Type[ModelType],
    filtros: Optional[Dict[str, Any]] = None
) -> int:
    """
    Contar registros con filtros opcionales
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        filtros: Diccionario de filtros {campo: valor}
        
    Returns:
        Número total de registros
    """
    try:
        query = db.query(func.count()).select_from(model)
        
        if filtros:
            for field, val in filtros.items():
                if hasattr(model, field):
                    query = query.filter(getattr(model, field) == val)
        
        return query.scalar()
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al contar registros: {str(e)}"
        )


def actualizar_registro(
    db: Session, 
    instancia: ModelType, 
    update_data: dict,
    exclude_unset: bool = True,
    commit: bool = True
) -> ModelType:
    """
    Actualizar un registro existente
    
    Args:
        db: Sesión de base de datos
        instancia: Instancia del modelo a actualizar
        update_data: Diccionario con los datos a actualizar
        exclude_unset: Si excluye campos None del update_data
        commit: Si hace commit inmediatamente
        
    Returns:
        Instancia actualizada
        
    Raises:
        HTTPException: Si hay error de integridad o actualización
    """
    try:
        # Filtrar campos None si exclude_unset=True
        if exclude_unset:
            update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Actualizar solo campos que existan en el modelo
        for field, value in update_data.items():
            if hasattr(instancia, field):
                setattr(instancia, field, value)
        
        if commit:
            db.commit()
            db.refresh(instancia)
        
        return instancia
        
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        
        if "UNIQUE" in error_msg or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un registro con esos datos únicos"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Error de integridad: {error_msg}"
            )
            
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar registro: {str(e)}"
        )


def eliminar_registro(
    db: Session, 
    instancia: ModelType, 
    soft_delete_field: Optional[str] = "Activo",
    commit: bool = True
) -> bool:
    """
    Eliminar un registro (soft delete o hard delete)
    
    Args:
        db: Sesión de base de datos
        instancia: Instancia del modelo a eliminar
        soft_delete_field: Campo para soft delete (ej: 'Activo'). 
                          Si es None, hace hard delete
        commit: Si hace commit inmediatamente
        
    Returns:
        True si se eliminó correctamente
        
    Raises:
        HTTPException: Si hay error al eliminar
    """
    try:
        if soft_delete_field and hasattr(instancia, soft_delete_field):
            # Soft delete: marcar como inactivo
            setattr(instancia, soft_delete_field, False)
            
            if commit:
                db.commit()
                db.refresh(instancia)
        else:
            # Hard delete: eliminar permanentemente
            db.delete(instancia)
            
            if commit:
                db.commit()
        
        return True
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar: existen registros relacionados"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar registro: {str(e)}"
        )


def restaurar_registro(
    db: Session,
    instancia: ModelType,
    soft_delete_field: str = "Activo",
    commit: bool = True
) -> ModelType:
    """
    Restaurar un registro eliminado con soft delete
    
    Args:
        db: Sesión de base de datos
        instancia: Instancia del modelo a restaurar
        soft_delete_field: Campo de soft delete (ej: 'Activo')
        commit: Si hace commit inmediatamente
        
    Returns:
        Instancia restaurada
    """
    try:
        if hasattr(instancia, soft_delete_field):
            setattr(instancia, soft_delete_field, True)
            
            if commit:
                db.commit()
                db.refresh(instancia)
            
            return instancia
        else:
            raise HTTPException(
                status_code=400,
                detail=f"El modelo no tiene campo '{soft_delete_field}'"
            )
            
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al restaurar registro: {str(e)}"
        )


# =============================================
# OPERACIONES AVANZADAS
# =============================================

def buscar_registros(
    db: Session,
    model: Type[ModelType],
    termino_busqueda: str,
    campos_busqueda: List[str],
    filtros_adicionales: Optional[Dict[str, Any]] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ModelType]:
    """
    Búsqueda avanzada en múltiples campos
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        termino_busqueda: Texto a buscar
        campos_busqueda: Lista de campos donde buscar
        filtros_adicionales: Filtros exactos adicionales
        skip: Paginación - registros a saltar
        limit: Paginación - máximo de registros
        
    Returns:
        Lista de instancias que coinciden con la búsqueda
        
    Example:
        # Buscar "juan" en nombre o email de usuarios activos
        usuarios = buscar_registros(
            db, Usuario,
            termino_busqueda="juan",
            campos_busqueda=["NombreCompleto", "Email"],
            filtros_adicionales={"Activo": True}
        )
    """
    try:
        query = db.query(model)
        
        # Aplicar filtros adicionales
        if filtros_adicionales:
            for field, val in filtros_adicionales.items():
                if hasattr(model, field):
                    query = query.filter(getattr(model, field) == val)
        
        # Crear condiciones de búsqueda con OR
        condiciones = []
        for campo in campos_busqueda:
            if hasattr(model, campo):
                condiciones.append(
                    getattr(model, campo).like(f"%{termino_busqueda}%")
                )
        
        if condiciones:
            query = query.filter(or_(*condiciones))
        
        return query.offset(skip).limit(limit).all()
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )


def existe_registro(
    db: Session,
    model: Type[ModelType],
    campo: str,
    valor: Any,
    excluir_id: Optional[int] = None,
    id_field: str = "IdProducto"
) -> bool:
    """
    Verificar si existe un registro con un valor específico en un campo
    Útil para validar unicidad antes de crear/actualizar
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        campo: Campo a verificar
        valor: Valor a buscar
        excluir_id: ID a excluir de la búsqueda (útil en actualizaciones)
        id_field: Nombre del campo ID
        
    Returns:
        True si existe, False si no
        
    Example:
        # Verificar si email ya existe (excluyendo usuario actual)
        existe = existe_registro(
            db, Usuario,
            campo="Email",
            valor="nuevo@email.com",
            excluir_id=user_id,
            id_field="IdUsuario"
        )
    """
    try:
        query = db.query(model).filter(getattr(model, campo) == valor)
        
        # Excluir un ID específico (útil para updates)
        if excluir_id is not None and hasattr(model, id_field):
            query = query.filter(getattr(model, id_field) != excluir_id)
        
        return db.query(query.exists()).scalar()
        
    except AttributeError:
        return False


def obtener_o_crear(
    db: Session,
    model: Type[ModelType],
    defaults: Optional[Dict[str, Any]] = None,
    commit: bool = True,
    **kwargs
) -> tuple[ModelType, bool]:
    """
    Obtener un registro existente o crear uno nuevo si no existe
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        defaults: Valores por defecto si se crea el registro
        commit: Si hace commit inmediatamente
        **kwargs: Filtros para buscar el registro
        
    Returns:
        Tupla (instancia, created) donde created es True si se creó
        
    Example:
        categoria, created = obtener_o_crear(
            db, Categoria,
            defaults={"Descripcion": "Descripción por defecto"},
            NombreCategoria="Bebidas"
        )
    """
    try:
        # Buscar registro existente
        query = db.query(model)
        for field, val in kwargs.items():
            if hasattr(model, field):
                query = query.filter(getattr(model, field) == val)
        
        instancia = query.first()
        
        if instancia:
            return instancia, False
        
        # Crear nuevo registro
        crear_data = kwargs.copy()
        if defaults:
            crear_data.update(defaults)
        
        instancia = model(**crear_data)
        db.add(instancia)
        
        if commit:
            db.commit()
            db.refresh(instancia)
        
        return instancia, True
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error en obtener_o_crear: {str(e)}"
        )


def actualizar_o_crear(
    db: Session,
    model: Type[ModelType],
    filtros: Dict[str, Any],
    update_data: Dict[str, Any],
    commit: bool = True
) -> tuple[ModelType, bool]:
    """
    Actualizar un registro existente o crear uno nuevo
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        filtros: Filtros para buscar el registro
        update_data: Datos para actualizar/crear
        commit: Si hace commit inmediatamente
        
    Returns:
        Tupla (instancia, created) donde created es True si se creó
    """
    try:
        # Buscar registro
        query = db.query(model)
        for field, val in filtros.items():
            if hasattr(model, field):
                query = query.filter(getattr(model, field) == val)
        
        instancia = query.first()
        
        if instancia:
            # Actualizar existente
            for field, value in update_data.items():
                if hasattr(instancia, field):
                    setattr(instancia, field, value)
            created = False
        else:
            # Crear nuevo
            crear_data = {**filtros, **update_data}
            instancia = model(**crear_data)
            db.add(instancia)
            created = True
        
        if commit:
            db.commit()
            db.refresh(instancia)
        
        return instancia, created
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error en actualizar_o_crear: {str(e)}"
        )


# =============================================
# OPERACIONES MASIVAS
# =============================================

def crear_multiples(
    db: Session,
    model: Type[ModelType],
    registros: List[Dict[str, Any]],
    commit: bool = True
) -> List[ModelType]:
    """
    Crear múltiples registros en una sola transacción
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        registros: Lista de diccionarios con datos
        commit: Si hace commit inmediatamente
        
    Returns:
        Lista de instancias creadas
    """
    try:
        instancias = [model(**datos) for datos in registros]
        db.add_all(instancias)
        
        if commit:
            db.commit()
            for inst in instancias:
                db.refresh(inst)
        
        return instancias
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear múltiples registros: {str(e)}"
        )


def eliminar_multiples(
    db: Session,
    model: Type[ModelType],
    ids: List[Any],
    id_field: str,
    soft_delete_field: Optional[str] = "Activo",
    commit: bool = True
) -> int:
    """
    Eliminar múltiples registros
    
    Args:
        db: Sesión de base de datos
        model: Clase del modelo
        ids: Lista de IDs a eliminar
        id_field: Nombre del campo ID
        soft_delete_field: Campo para soft delete (None para hard delete)
        commit: Si hace commit inmediatamente
        
    Returns:
        Número de registros eliminados
    """
    try:
        query = db.query(model).filter(getattr(model, id_field).in_(ids))
        
        if soft_delete_field and hasattr(model, soft_delete_field):
            # Soft delete
            count = query.update(
                {soft_delete_field: False},
                synchronize_session=False
            )
        else:
            # Hard delete
            count = query.delete(synchronize_session=False)
        
        if commit:
            db.commit()
        
        return count
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar múltiples registros: {str(e)}"
        )