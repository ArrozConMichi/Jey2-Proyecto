"""
Router para operaciones CRUD de proveedores
Gestión completa de proveedores con validaciones y búsqueda avanzada
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas, crud
from app.routers.auth import get_current_active_user

router = APIRouter()

# =============================================
# ENDPOINTS DE PROVEEDORES
# =============================================

@router.get("/", response_model=List[schemas.ProveedorOut])
def listar_proveedores(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre, RUC o contacto"),
    ordenar_por: str = Query("NombreProveedor", description="Campo para ordenar"),
    orden_desc: bool = Query(False, description="Orden descendente"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Listar todos los proveedores con filtros opcionales y paginación
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Máximo de registros a retornar
    - **activo**: Filtrar por proveedores activos/inactivos
    - **buscar**: Buscar en nombre, RUC o contacto principal
    - **ordenar_por**: Campo para ordenar resultados
    - **orden_desc**: Si el orden es descendente
    """
    try:
        # Construir filtros
        filtros = {}
        if activo is not None:
            filtros["Activo"] = activo
        
        # Búsqueda avanzada si se proporciona término
        if buscar:
            proveedores = crud.buscar_registros(
                db=db,
                model=models.Proveedor,
                termino_busqueda=buscar,
                campos_busqueda=["NombreProveedor", "RUC", "ContactoPrincipal", "Email"],
                filtros_adicionales=filtros,
                skip=skip,
                limit=limit
            )
        else:
            # Listado normal con filtros
            proveedores = crud.listar_registros(
                db=db,
                model=models.Proveedor,
                skip=skip,
                limit=limit,
                filtros=filtros,
                ordenar_por=ordenar_por,
                orden_desc=orden_desc
            )
        
        return proveedores
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar proveedores: {str(e)}"
        )


@router.get("/stats", response_model=dict)
def obtener_estadisticas_proveedores(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas generales de proveedores
    """
    total = crud.contar_registros(db, models.Proveedor)
    activos = crud.contar_registros(db, models.Proveedor, filtros={"Activo": True})
    inactivos = crud.contar_registros(db, models.Proveedor, filtros={"Activo": False})
    
    # Proveedores con más órdenes de compra
    top_proveedores = db.query(
        models.Proveedor.NombreProveedor,
        db.func.count(models.OrdenCompra.IdOrdenCompra).label("total_ordenes")
    ).join(
        models.OrdenCompra
    ).group_by(
        models.Proveedor.IdProveedor,
        models.Proveedor.NombreProveedor
    ).order_by(
        db.func.count(models.OrdenCompra.IdOrdenCompra).desc()
    ).limit(5).all()
    
    return {
        "total_proveedores": total,
        "activos": activos,
        "inactivos": inactivos,
        "top_proveedores": [
            {"nombre": nombre, "total_ordenes": total}
            for nombre, total in top_proveedores
        ]
    }


@router.get("/buscar/ruc/{ruc}", response_model=schemas.ProveedorOut)
def buscar_proveedor_por_ruc(
    ruc: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Buscar un proveedor por su RUC
    """
    proveedor = crud.obtener_por_campo(
        db=db,
        model=models.Proveedor,
        campo="RUC",
        valor=ruc,
        raise_not_found=True
    )
    return proveedor


@router.get("/{proveedor_id}", response_model=schemas.ProveedorOut)
def obtener_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener un proveedor específico por su ID
    """
    proveedor = crud.obtener_registro(
        db=db,
        model=models.Proveedor,
        id_field="IdProveedor",
        id_val=proveedor_id,
        raise_not_found=True
    )
    return proveedor


@router.get("/{proveedor_id}/ordenes")
def obtener_ordenes_proveedor(
    proveedor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    estado: Optional[str] = Query(None, description="Filtrar por estado de orden"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener todas las órdenes de compra de un proveedor específico
    """
    # Verificar que el proveedor existe
    proveedor = crud.obtener_registro(
        db=db,
        model=models.Proveedor,
        id_field="IdProveedor",
        id_val=proveedor_id,
        raise_not_found=True
    )
    
    # Construir filtros
    filtros = {"IdProveedor": proveedor_id}
    if estado:
        filtros["EstadoOrden"] = estado
    
    # Obtener órdenes
    ordenes = crud.listar_registros(
        db=db,
        model=models.OrdenCompra,
        skip=skip,
        limit=limit,
        filtros=filtros,
        ordenar_por="FechaOrden",
        orden_desc=True
    )
    
    # Contar total
    total = crud.contar_registros(
        db=db,
        model=models.OrdenCompra,
        filtros=filtros
    )
    
    return {
        "proveedor": proveedor.NombreProveedor,
        "total_ordenes": total,
        "ordenes": ordenes
    }


@router.post("/", response_model=schemas.ProveedorOut, status_code=status.HTTP_201_CREATED)
def crear_proveedor(
    proveedor: schemas.ProveedorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo proveedor
    
    Validaciones:
    - El RUC debe ser único (si se proporciona)
    - El nombre del proveedor es obligatorio
    """
    # Validar que el RUC no exista (si se proporciona)
    if proveedor.RUC:
        if crud.existe_registro(
            db=db,
            model=models.Proveedor,
            campo="RUC",
            valor=proveedor.RUC
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un proveedor con el RUC {proveedor.RUC}"
            )
    
    # Validar email único si se proporciona
    if proveedor.Email:
        if crud.existe_registro(
            db=db,
            model=models.Proveedor,
            campo="Email",
            valor=proveedor.Email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un proveedor con el email {proveedor.Email}"
            )
    
    # Crear proveedor
    nuevo_proveedor = crud.crear_registro(
        db=db,
        model=models.Proveedor,
        obj_data=proveedor.dict()
    )
    
    return nuevo_proveedor


@router.put("/{proveedor_id}", response_model=schemas.ProveedorOut)
def actualizar_proveedor(
    proveedor_id: int,
    proveedor_update: schemas.ProveedorUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un proveedor existente
    
    Solo se actualizan los campos proporcionados (exclude_unset=True)
    """
    # Obtener proveedor existente
    proveedor = crud.obtener_registro(
        db=db,
        model=models.Proveedor,
        id_field="IdProveedor",
        id_val=proveedor_id,
        raise_not_found=True
    )
    
    # Obtener datos a actualizar
    update_data = proveedor_update.dict(exclude_unset=True)
    
    # Validar RUC único si se está actualizando
    if "RUC" in update_data and update_data["RUC"]:
        if crud.existe_registro(
            db=db,
            model=models.Proveedor,
            campo="RUC",
            valor=update_data["RUC"],
            excluir_id=proveedor_id,
            id_field="IdProveedor"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otro proveedor con el RUC {update_data['RUC']}"
            )
    
    # Validar Email único si se está actualizando
    if "Email" in update_data and update_data["Email"]:
        if crud.existe_registro(
            db=db,
            model=models.Proveedor,
            campo="Email",
            valor=update_data["Email"],
            excluir_id=proveedor_id,
            id_field="IdProveedor"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otro proveedor con el email {update_data['Email']}"
            )
    
    # Actualizar proveedor
    proveedor_actualizado = crud.actualizar_registro(
        db=db,
        instancia=proveedor,
        update_data=update_data
    )
    
    return proveedor_actualizado


@router.delete("/{proveedor_id}")
def eliminar_proveedor(
    proveedor_id: int,
    forzar: bool = Query(False, description="Forzar eliminación aunque tenga órdenes"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Eliminar (desactivar) un proveedor
    
    - Por defecto hace soft delete (marca como inactivo)
    - Si tiene órdenes de compra asociadas, no se puede eliminar a menos que se fuerce
    """
    # Verificar permisos (solo administradores pueden eliminar)
    if current_user.IdRol != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar proveedores"
        )
    
    # Obtener proveedor
    proveedor = crud.obtener_registro(
        db=db,
        model=models.Proveedor,
        id_field="IdProveedor",
        id_val=proveedor_id,
        raise_not_found=True
    )
    
    # Verificar si tiene órdenes de compra asociadas
    tiene_ordenes = crud.contar_registros(
        db=db,
        model=models.OrdenCompra,
        filtros={"IdProveedor": proveedor_id}
    ) > 0
    
    if tiene_ordenes and not forzar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "El proveedor tiene órdenes de compra asociadas. "
                "Use el parámetro 'forzar=true' para desactivarlo de todas formas."
            )
        )
    
    # Soft delete
    crud.eliminar_registro(
        db=db,
        instancia=proveedor,
        soft_delete_field="Activo"
    )
    
    return {
        "mensaje": "Proveedor eliminado correctamente",
        "id_proveedor": proveedor_id,
        "nombre": proveedor.NombreProveedor
    }


@router.post("/{proveedor_id}/activar")
def activar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Reactivar un proveedor desactivado
    """
    # Verificar permisos
    if current_user.IdRol != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para activar proveedores"
        )
    
    # Obtener proveedor
    proveedor = crud.obtener_registro(
        db=db,
        model=models.Proveedor,
        id_field="IdProveedor",
        id_val=proveedor_id,
        raise_not_found=True
    )
    
    # Verificar si ya está activo
    if proveedor.Activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El proveedor ya está activo"
        )
    
    # Restaurar
    proveedor_restaurado = crud.restaurar_registro(
        db=db,
        instancia=proveedor,
        soft_delete_field="Activo"
    )
    
    return {
        "mensaje": "Proveedor activado correctamente",
        "proveedor": proveedor_restaurado
    }


@router.get("/{proveedor_id}/resumen-compras")
def resumen_compras_proveedor(
    proveedor_id: int,
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener resumen de compras realizadas a un proveedor
    
    Incluye:
    - Total de órdenes
    - Monto total comprado
    - Órdenes por estado
    - Productos más comprados
    """
    # Verificar que el proveedor existe
    proveedor = crud.obtener_registro(
        db=db,
        model=models.Proveedor,
        id_field="IdProveedor",
        id_val=proveedor_id,
        raise_not_found=True
    )
    
    # Query base
    query = db.query(models.OrdenCompra).filter(
        models.OrdenCompra.IdProveedor == proveedor_id
    )
    
    # Filtrar por fechas si se proporcionan
    if fecha_inicio:
        query = query.filter(models.OrdenCompra.FechaOrden >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.OrdenCompra.FechaOrden <= fecha_fin)
    
    ordenes = query.all()
    
    # Calcular estadísticas
    total_ordenes = len(ordenes)
    monto_total = sum(orden.Total for orden in ordenes)
    
    # Contar por estado
    estados = {}
    for orden in ordenes:
        estados[orden.EstadoOrden] = estados.get(orden.EstadoOrden, 0) + 1
    
    # Productos más comprados
    productos_query = db.query(
        models.Producto.NombreProducto,
        db.func.sum(models.DetalleOrdenCompra.Cantidad).label("cantidad_total"),
        db.func.sum(models.DetalleOrdenCompra.SubTotal).label("monto_total")
    ).join(
        models.DetalleOrdenCompra
    ).join(
        models.OrdenCompra
    ).filter(
        models.OrdenCompra.IdProveedor == proveedor_id
    ).group_by(
        models.Producto.IdProducto,
        models.Producto.NombreProducto
    ).order_by(
        db.func.sum(models.DetalleOrdenCompra.Cantidad).desc()
    ).limit(10).all()
    
    return {
        "proveedor": {
            "id": proveedor.IdProveedor,
            "nombre": proveedor.NombreProveedor,
            "ruc": proveedor.RUC
        },
        "periodo": {
            "fecha_inicio": fecha_inicio or "Sin filtro",
            "fecha_fin": fecha_fin or "Sin filtro"
        },
        "resumen": {
            "total_ordenes": total_ordenes,
            "monto_total": float(monto_total),
            "ordenes_por_estado": estados,
            "promedio_por_orden": float(monto_total / total_ordenes) if total_ordenes > 0 else 0
        },
        "productos_mas_comprados": [
            {
                "producto": nombre,
                "cantidad_total": int(cantidad),
                "monto_total": float(monto)
            }
            for nombre, cantidad, monto in productos_query
        ]
    }


@router.post("/crear-multiple", response_model=List[schemas.ProveedorOut])
def crear_proveedores_multiples(
    proveedores: List[schemas.ProveedorCreate],
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear múltiples proveedores en una sola operación
    
    Útil para importaciones masivas
    """
    # Verificar permisos
    if current_user.IdRol != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear proveedores masivamente"
        )
    
    # Validar que no haya RUCs duplicados en el lote
    rucs = [p.RUC for p in proveedores if p.RUC]
    if len(rucs) != len(set(rucs)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hay RUCs duplicados en los datos proporcionados"
        )
    
    # Validar que los RUCs no existan en BD
    for ruc in rucs:
        if crud.existe_registro(db, models.Proveedor, "RUC", ruc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El RUC {ruc} ya existe en la base de datos"
            )
    
    # Crear proveedores
    registros = [p.dict() for p in proveedores]
    nuevos_proveedores = crud.crear_multiples(
        db=db,
        model=models.Proveedor,
        registros=registros
    )
    
    return nuevos_proveedores