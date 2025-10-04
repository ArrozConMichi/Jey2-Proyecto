"""
Modelos SQLAlchemy para el sistema Jey2
Mapean las tablas de SQL Server a clases Python
"""
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, ForeignKey, Date, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# =============================================
# MÓDULO DE SEGURIDAD Y USUARIOS
# =============================================

class Rol(Base):
    __tablename__ = "Roles"
    
    IdRol = Column(Integer, primary_key=True, index=True)
    NombreRol = Column(String(50), unique=True, nullable=False)
    Descripcion = Column(String(200))
    FechaCreacion = Column(DateTime, server_default=func.getdate())
    Activo = Column(Boolean, default=True)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "Usuarios"
    
    IdUsuario = Column(Integer, primary_key=True, index=True)
    NombreUsuario = Column(String(50), unique=True, nullable=False, index=True)
    ContrasenaHash = Column(LargeBinary(256), nullable=False)
    NombreCompleto = Column(String(100), nullable=False)
    Email = Column(String(100))
    IdRol = Column(Integer, ForeignKey("Roles.IdRol"), nullable=False)
    IntentosLogin = Column(Integer, default=0)
    Bloqueado = Column(Boolean, default=False)
    FechaCreacion = Column(DateTime, server_default=func.getdate())
    UltimoAcceso = Column(DateTime)
    Activo = Column(Boolean, default=True)
    FotoPerfilURL = Column(String(500))
    FotoTipo = Column(String(10))
    FechaSubidaFoto = Column(DateTime)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    ventas = relationship("Venta", back_populates="usuario")
    movimientos_inventario = relationship("MovimientoInventario", back_populates="usuario")


# =============================================
# MÓDULO DE INVENTARIO
# =============================================

class Categoria(Base):
    __tablename__ = "Categorias"
    
    IdCategoria = Column(Integer, primary_key=True, index=True)
    NombreCategoria = Column(String(100), nullable=False)
    Descripcion = Column(String(200))
    Activo = Column(Boolean, default=True)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria")


class UnidadMedida(Base):
    __tablename__ = "UnidadesMedida"
    
    IdUnidad = Column(Integer, primary_key=True, index=True)
    NombreUnidad = Column(String(50), unique=True, nullable=False)
    Abreviatura = Column(String(10), nullable=False)
    Activo = Column(Boolean, default=True)
    
    # Relaciones
    productos = relationship("Producto", back_populates="unidad")


class Producto(Base):
    __tablename__ = "Productos"
    
    IdProducto = Column(Integer, primary_key=True, index=True)
    CodigoBarras = Column(String(50), unique=True, index=True)
    NombreProducto = Column(String(200), nullable=False, index=True)
    Descripcion = Column(String(500))
    IdCategoria = Column(Integer, ForeignKey("Categorias.IdCategoria"), nullable=False)
    IdUnidad = Column(Integer, ForeignKey("UnidadesMedida.IdUnidad"), nullable=False)
    PrecioCompra = Column(DECIMAL(10, 2), nullable=False)
    PrecioVenta = Column(DECIMAL(10, 2), nullable=False)
    StockActual = Column(Integer, nullable=False, default=0, index=True)
    StockMinimo = Column(Integer, nullable=False, default=5)
    StockMaximo = Column(Integer)
    FechaVencimiento = Column(Date)
    Lote = Column(String(50))
    Ubicacion = Column(String(100))
    FechaCreacion = Column(DateTime, server_default=func.getdate())
    FechaActualizacion = Column(DateTime, server_default=func.getdate())
    Activo = Column(Boolean, default=True)
    ImagenURL = Column(String(500))
    ImagenTipo = Column(String(10))
    FechaSubidaImagen = Column(DateTime)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    unidad = relationship("UnidadMedida", back_populates="productos")
    detalles_venta = relationship("DetalleVenta", back_populates="producto")
    movimientos_inventario = relationship("MovimientoInventario", back_populates="producto")
    imagenes = relationship("ImagenProducto", back_populates="producto")


class ImagenProducto(Base):
    __tablename__ = "ImagenesProducto"
    
    IdImagenProducto = Column(Integer, primary_key=True, index=True)
    IdProducto = Column(Integer, ForeignKey("Productos.IdProducto"), nullable=False, index=True)
    ImagenURL = Column(String(500), nullable=False)
    ImagenTipo = Column(String(10), nullable=False)
    ImagenNombre = Column(String(100), nullable=False)
    EsPrincipal = Column(Boolean, default=False)
    Orden = Column(Integer, default=1)
    FechaSubida = Column(DateTime, server_default=func.getdate())
    Activo = Column(Boolean, default=True)
    
    # Relaciones
    producto = relationship("Producto", back_populates="imagenes")


class MovimientoInventario(Base):
    __tablename__ = "MovimientosInventario"
    
    IdMovimiento = Column(Integer, primary_key=True, index=True)
    IdProducto = Column(Integer, ForeignKey("Productos.IdProducto"), nullable=False, index=True)
    TipoMovimiento = Column(String(20), nullable=False)  # ENTRADA, SALIDA, AJUSTE
    Cantidad = Column(Integer, nullable=False)
    StockAnterior = Column(Integer, nullable=False)
    StockNuevo = Column(Integer, nullable=False)
    Motivo = Column(String(200))
    IdUsuario = Column(Integer, ForeignKey("Usuarios.IdUsuario"), nullable=False)
    FechaMovimiento = Column(DateTime, server_default=func.getdate())
    Referencia = Column(String(100))
    
    # Relaciones
    producto = relationship("Producto", back_populates="movimientos_inventario")
    usuario = relationship("Usuario", back_populates="movimientos_inventario")


# =============================================
# MÓDULO DE PROVEEDORES
# =============================================

class Proveedor(Base):
    __tablename__ = "Proveedores"
    
    IdProveedor = Column(Integer, primary_key=True, index=True)
    NombreProveedor = Column(String(200), nullable=False, index=True)
    RUC = Column(String(30), unique=True)
    Telefono = Column(String(30))
    Email = Column(String(100))
    Direccion = Column(String(300))
    ContactoPrincipal = Column(String(100))
    TelefonoContacto = Column(String(30))
    FechaRegistro = Column(DateTime, server_default=func.getdate())
    Activo = Column(Boolean, default=True)
    LogoURL = Column(String(500))
    LogoTipo = Column(String(10))
    FechaSubidaLogo = Column(DateTime)
    
    # Relaciones
    ordenes_compra = relationship("OrdenCompra", back_populates="proveedor")


class OrdenCompra(Base):
    __tablename__ = "OrdenesCompra"
    
    IdOrdenCompra = Column(Integer, primary_key=True, index=True)
    NumeroOrden = Column(String(50), unique=True, nullable=False, index=True)
    IdProveedor = Column(Integer, ForeignKey("Proveedores.IdProveedor"), nullable=False)
    FechaOrden = Column(DateTime, server_default=func.getdate())
    FechaEntregaEstimada = Column(Date)
    EstadoOrden = Column(String(20), nullable=False, default='PENDIENTE', index=True)
    SubTotal = Column(DECIMAL(12, 2), nullable=False)
    Impuesto = Column(DECIMAL(12, 2), default=0)
    Total = Column(DECIMAL(12, 2), nullable=False)
    IdUsuarioCreacion = Column(Integer, ForeignKey("Usuarios.IdUsuario"), nullable=False)
    Observaciones = Column(String(500))
    
    # Relaciones
    proveedor = relationship("Proveedor", back_populates="ordenes_compra")
    detalles = relationship("DetalleOrdenCompra", back_populates="orden_compra")


class DetalleOrdenCompra(Base):
    __tablename__ = "DetallesOrdenCompra"
    
    IdDetalleOrden = Column(Integer, primary_key=True, index=True)
    IdOrdenCompra = Column(Integer, ForeignKey("OrdenesCompra.IdOrdenCompra"), nullable=False)
    IdProducto = Column(Integer, ForeignKey("Productos.IdProducto"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    PrecioUnitario = Column(DECIMAL(10, 2), nullable=False)
    SubTotal = Column(DECIMAL(12, 2), nullable=False)
    CantidadRecibida = Column(Integer, default=0)
    
    # Relaciones
    orden_compra = relationship("OrdenCompra", back_populates="detalles")


# =============================================
# MÓDULO DE VENTAS
# =============================================

class Cliente(Base):
    __tablename__ = "Clientes"
    
    IdCliente = Column(Integer, primary_key=True, index=True)
    TipoDocumento = Column(String(20))  # CEDULA, RUC, PASAPORTE
    NumeroDocumento = Column(String(30), unique=True, index=True)
    NombreCompleto = Column(String(200), nullable=False, index=True)
    Telefono = Column(String(30))
    Email = Column(String(100))
    Direccion = Column(String(300))
    FechaRegistro = Column(DateTime, server_default=func.getdate())
    Activo = Column(Boolean, default=True)
    
    # Relaciones
    ventas = relationship("Venta", back_populates="cliente")


class MetodoPago(Base):
    __tablename__ = "MetodosPago"
    
    IdMetodoPago = Column(Integer, primary_key=True, index=True)
    NombreMetodo = Column(String(50), unique=True, nullable=False)
    Descripcion = Column(String(100))
    Activo = Column(Boolean, default=True)
    
    # Relaciones
    ventas = relationship("Venta", back_populates="metodo_pago")


class Venta(Base):
    __tablename__ = "Ventas"
    
    IdVenta = Column(Integer, primary_key=True, index=True)
    NumeroVenta = Column(String(50), unique=True, nullable=False, index=True)
    FechaVenta = Column(DateTime, server_default=func.getdate(), index=True)
    IdCliente = Column(Integer, ForeignKey("Clientes.IdCliente"))
    IdUsuario = Column(Integer, ForeignKey("Usuarios.IdUsuario"), nullable=False)
    SubTotal = Column(DECIMAL(12, 2), nullable=False)
    Descuento = Column(DECIMAL(12, 2), default=0)
    Impuesto = Column(DECIMAL(12, 2), default=0)
    Total = Column(DECIMAL(12, 2), nullable=False)
    IdMetodoPago = Column(Integer, ForeignKey("MetodosPago.IdMetodoPago"), nullable=False)
    EstadoVenta = Column(String(20), nullable=False, default='COMPLETADA')
    Observaciones = Column(String(500))
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="ventas")
    usuario = relationship("Usuario", back_populates="ventas")
    metodo_pago = relationship("MetodoPago", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "DetallesVenta"
    
    IdDetalleVenta = Column(Integer, primary_key=True, index=True)
    IdVenta = Column(Integer, ForeignKey("Ventas.IdVenta"), nullable=False)
    IdProducto = Column(Integer, ForeignKey("Productos.IdProducto"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    PrecioUnitario = Column(DECIMAL(10, 2), nullable=False)
    Descuento = Column(DECIMAL(10, 2), default=0)
    SubTotal = Column(DECIMAL(12, 2), nullable=False)
    
    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")


# =============================================
# CONFIGURACIÓN
# =============================================

class ConfiguracionSistema(Base):
    __tablename__ = "ConfiguracionSistema"
    
    IdConfig = Column(Integer, primary_key=True, index=True)
    ClaveConfig = Column(String(100), unique=True, nullable=False, index=True)
    ValorConfig = Column(String(500))
    Descripcion = Column(String(200))
    FechaActualizacion = Column(DateTime, server_default=func.getdate())