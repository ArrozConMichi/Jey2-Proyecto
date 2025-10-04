"""
Router para operaciones CRUD de productos
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter()

# =============================================
# ENDPOINTS DE PRODUCTOS
# =============================================

@router.get("/", response_model=List[schemas.ProductoOut])
def listar_productos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    categoria: Optional[int] = Query(None, description="Filtrar por categoría"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre o código"),
    db: Session = Depends(get_db)
):
    """
    Listar todos los productos con filtros opcionales
    """
    query = db.query(models.Producto)
    
    # Aplicar filtros
    if activo is not None:
        query = query.filter(models.Producto.Activo == activo)
    
    if categoria:
        query = query.filter(models.Producto.IdCategoria == categoria)
    
    if buscar:
        query = query.filter(
            (models.Producto.NombreProducto.like(f"%{buscar}%")) |
            (models.Producto.CodigoBarras.like(f"%{buscar}%"))
        )
    
    # Paginación
    productos = query.offset(skip).limit(limit).all()
    return productos


@router.get("/{id_producto}", response_model=schemas.ProductoOut)
def obtener_producto(
    id_producto: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un producto específico por ID
    """
    producto = db.query(models.Producto).filter(
        models.Producto.IdProducto == id_producto
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto


@router.get("/codigo/{codigo_barras}", response_model=schemas.ProductoOut)
def obtener_producto_por_codigo(
    codigo_barras: str,
    db: Session = Depends(get_db)
):
    """
    Obtener un producto por su código de barras
    """
    producto = db.query(models.Producto).filter(
        models.Producto.CodigoBarras == codigo_barras,
        models.Producto.Activo == True
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto


@router.post("/", response_model=schemas.ProductoOut, status_code=201)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo producto
    """
    # Verificar si el código de barras ya existe
    if producto.CodigoBarras:
        existe = db.query(models.Producto).filter(
            models.Producto.CodigoBarras == producto.CodigoBarras
        ).first()
        if existe:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un producto con ese código de barras"
            )
    
    # Verificar que precio de venta sea mayor o igual al de compra
    if producto.PrecioVenta < producto.PrecioCompra:
        raise HTTPException(
            status_code=400,
            detail="El precio de venta debe ser mayor o igual al precio de compra"
        )
    
    # Crear nuevo producto
    nuevo_producto = models.Producto(**producto.dict())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    
    return nuevo_producto


@router.put("/{id_producto}", response_model=schemas.ProductoOut)
def actualizar_producto(
    id_producto: int,
    producto_update: schemas.ProductoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un producto existente
    """
    producto = db.query(models.Producto).filter(
        models.Producto.IdProducto == id_producto
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualizar solo los campos proporcionados
    update_data = producto_update.dict(exclude_unset=True)
    
    # Validar precios si se actualizan
    precio_venta = update_data.get('PrecioVenta', producto.PrecioVenta)
    precio_compra = update_data.get('PrecioCompra', producto.PrecioCompra)
    
    if precio_venta < precio_compra:
        raise HTTPException(
            status_code=400,
            detail="El precio de venta debe ser mayor o igual al precio de compra"
        )
    
    for field, value in update_data.items():
        setattr(producto, field, value)
    
    db.commit()
    db.refresh(producto)
    
    return producto


@router.delete("/{id_producto}")
def eliminar_producto(
    id_producto: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar (desactivar) un producto
    """
    producto = db.query(models.Producto).filter(
        models.Producto.IdProducto == id_producto
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Soft delete - solo marcar como inactivo
    producto.Activo = False
    db.commit()
    
    return {"mensaje": "Producto eliminado correctamente"}


@router.get("/stock-bajo/", response_model=List[schemas.ProductoStockBajo])
def productos_con_stock_bajo(
    db: Session = Depends(get_db)
):
    """
    Obtener productos con stock bajo (stock actual <= stock mínimo)
    """
    productos = db.query(models.Producto).filter(
        models.Producto.StockActual <= models.Producto.StockMinimo,
        models.Producto.Activo == True
    ).all()
    
    return productos


@router.patch("/{id_producto}/stock")
def ajustar_stock(
    id_producto: int,
    ajuste: schemas.AjusteStock,
    db: Session = Depends(get_db)
):
    """
    Ajustar el stock de un producto
    """
    producto = db.query(models.Producto).filter(
        models.Producto.IdProducto == id_producto
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    stock_anterior = producto.StockActual
    
    # Aplicar ajuste según el tipo
    if ajuste.tipo_movimiento == "ENTRADA":
        producto.StockActual += ajuste.cantidad
    elif ajuste.tipo_movimiento == "SALIDA":
        if producto.StockActual < ajuste.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        producto.StockActual -= ajuste.cantidad
    elif ajuste.tipo_movimiento == "AJUSTE":
        producto.StockActual = ajuste.cantidad
    
    # Registrar movimiento en el historial
    movimiento = models.MovimientoInventario(
        IdProducto=id_producto,
        TipoMovimiento=ajuste.tipo_movimiento,
        Cantidad=ajuste.cantidad,
        StockAnterior=stock_anterior,
        StockNuevo=producto.StockActual,
        Motivo=ajuste.motivo,
        IdUsuario=ajuste.id_usuario,
        Referencia=ajuste.referencia
    )
    
    db.add(movimiento)
    db.commit()
    db.refresh(producto)
    
    return {
        "mensaje": "Stock ajustado correctamente",
        "stock_anterior": stock_anterior,
        "stock_nuevo": producto.StockActual
    }