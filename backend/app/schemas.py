"""
Schemas Pydantic para validación de datos de entrada/salida
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# =============================================
# SCHEMAS DE PRODUCTOS
# =============================================

class ProductoBase(BaseModel):
    CodigoBarras: Optional[str] = Field(None, max_length=50)
    NombreProducto: str = Field(..., min_length=1, max_length=200)
    Descripcion: Optional[str] = Field(None, max_length=500)
    IdCategoria: int = Field(..., gt=0)
    IdUnidad: int = Field(..., gt=0)
    PrecioCompra: Decimal = Field(..., ge=0, decimal_places=2)
    PrecioVenta: Decimal = Field(..., ge=0, decimal_places=2)
    StockMinimo: int = Field(5, ge=0)
    StockMaximo: Optional[int] = Field(None, ge=0)
    FechaVencimiento: Optional[date] = None
    Lote: Optional[str] = Field(None, max_length=50)
    Ubicacion: Optional[str] = Field(None, max_length=100)
    
    @validator('PrecioVenta')
    def validar_precio_venta(cls, v, values):
        if 'PrecioCompra' in values and v < values['PrecioCompra']:
            raise ValueError('El precio de venta debe ser mayor o igual al precio de compra')
        return v
    
    @validator('PrecioCompra', 'PrecioVenta')
    def validar_decimales(cls, v):
        return round(v, 2)



class ProductoCreate(ProductoBase):
    StockActual: int = Field(0, ge=0)


class ProductoUpdate(BaseModel):
    CodigoBarras: Optional[str] = Field(None, max_length=50)
    NombreProducto: Optional[str] = Field(None, min_length=1, max_length=200)
    Descripcion: Optional[str] = Field(None, max_length=500)
    IdCategoria: Optional[int] = Field(None, gt=0)
    IdUnidad: Optional[int] = Field(None, gt=0)
    PrecioCompra: Optional[Decimal] = Field(None, ge=0)
    PrecioVenta: Optional[Decimal] = Field(None, ge=0)
    StockMinimo: Optional[int] = Field(None, ge=0)
    StockMaximo: Optional[int] = Field(None, ge=0)
    FechaVencimiento: Optional[date] = None
    Lote: Optional[str] = Field(None, max_length=50)
    Ubicacion: Optional[str] = Field(None, max_length=100)
    Activo: Optional[bool] = None


class ProductoOut(ProductoBase):
    IdProducto: int
    StockActual: int
    FechaCreacion: datetime
    FechaActualizacion: datetime
    Activo: bool
    ImagenURL: Optional[str] = None
    ImagenTipo: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductoStockBajo(BaseModel):
    IdProducto: int
    CodigoBarras: Optional[str]
    NombreProducto: str
    StockActual: int
    StockMinimo: int
    CantidadFaltante: int
    
    class Config:
        from_attributes = True


class AjusteStock(BaseModel):
    tipo_movimiento: str = Field(..., pattern="^(ENTRADA|SALIDA|AJUSTE)$")
    cantidad: int = Field(..., gt=0)
    motivo: Optional[str] = Field(None, max_length=200)
    id_usuario: int = Field(..., gt=0)
    referencia: Optional[str] = Field(None, max_length=100)


# =============================================
# SCHEMAS DE USUARIOS
# =============================================

class UsuarioBase(BaseModel):
    NombreUsuario: str = Field(..., min_length=3, max_length=50)
    NombreCompleto: str = Field(..., min_length=1, max_length=100)
    Email: Optional[EmailStr] = None
    IdRol: int = Field(..., gt=0)


class UsuarioCreate(UsuarioBase):
    Contrasena: str = Field(..., min_length=6, max_length=100)


class UsuarioUpdate(BaseModel):
    NombreCompleto: Optional[str] = Field(None, min_length=1, max_length=100)
    Email: Optional[EmailStr] = None
    IdRol: Optional[int] = Field(None, gt=0)
    Activo: Optional[bool] = None


class UsuarioOut(UsuarioBase):
    IdUsuario: int
    Bloqueado: bool
    FechaCreacion: datetime
    UltimoAcceso: Optional[datetime]
    Activo: bool
    FotoPerfilURL: Optional[str] = None
    
    class Config:
        from_attributes = True


class CambiarContrasena(BaseModel):
    contrasena_actual: str = Field(..., min_length=6)
    contrasena_nueva: str = Field(..., min_length=6)
    confirmar_contrasena: str = Field(..., min_length=6)
    
    @validator('confirmar_contrasena')
    def validar_contrasenas(cls, v, values):
        if 'contrasena_nueva' in values and v != values['contrasena_nueva']:
            raise ValueError('Las contraseñas no coinciden')
        return v


# =============================================
# SCHEMAS DE AUTENTICACIÓN
# =============================================

class Login(BaseModel):
    nombre_usuario: str = Field(..., min_length=3)
    contrasena: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioOut


class TokenData(BaseModel):
    username: Optional[str] = None
    id_usuario: Optional[int] = None


# =============================================
# SCHEMAS DE CATEGORÍAS
# =============================================

class CategoriaBase(BaseModel):
    NombreCategoria: str = Field(..., min_length=1, max_length=100)
    Descripcion: Optional[str] = Field(None, max_length=200)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaOut(CategoriaBase):
    IdCategoria: int
    Activo: bool
    
    class Config:
        from_attributes = True


# =============================================
# SCHEMAS DE PROVEEDORES
# =============================================

class ProveedorBase(BaseModel):
    NombreProveedor: str = Field(..., min_length=1, max_length=200)
    RUC: Optional[str] = Field(None, max_length=30)
    Telefono: Optional[str] = Field(None, max_length=30)
    Email: Optional[EmailStr] = None
    Direccion: Optional[str] = Field(None, max_length=300)
    ContactoPrincipal: Optional[str] = Field(None, max_length=100)
    TelefonoContacto: Optional[str] = Field(None, max_length=30)


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    NombreProveedor: Optional[str] = Field(None, min_length=1, max_length=200)
    RUC: Optional[str] = Field(None, max_length=30)
    Telefono: Optional[str] = Field(None, max_length=30)
    Email: Optional[EmailStr] = None
    Direccion: Optional[str] = Field(None, max_length=300)
    ContactoPrincipal: Optional[str] = Field(None, max_length=100)
    TelefonoContacto: Optional[str] = Field(None, max_length=30)
    Activo: Optional[bool] = None


class ProveedorOut(ProveedorBase):
    IdProveedor: int
    FechaRegistro: datetime
    Activo: bool
    LogoURL: Optional[str] = None
    
    class Config:
        from_attributes = True


# =============================================
# SCHEMAS DE CLIENTES
# =============================================

class ClienteBase(BaseModel):
    TipoDocumento: Optional[str] = Field(None, pattern="^(CEDULA|RUC|PASAPORTE)$")
    NumeroDocumento: Optional[str] = Field(None, max_length=30)
    NombreCompleto: str = Field(..., min_length=1, max_length=200)
    Telefono: Optional[str] = Field(None, max_length=30)
    Email: Optional[EmailStr] = None
    Direccion: Optional[str] = Field(None, max_length=300)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    TipoDocumento: Optional[str] = Field(None, pattern="^(CEDULA|RUC|PASAPORTE)$")
    NumeroDocumento: Optional[str] = Field(None, max_length=30)
    NombreCompleto: Optional[str] = Field(None, min_length=1, max_length=200)
    Telefono: Optional[str] = Field(None, max_length=30)
    Email: Optional[EmailStr] = None
    Direccion: Optional[str] = Field(None, max_length=300)
    Activo: Optional[bool] = None


class ClienteOut(ClienteBase):
    IdCliente: int
    FechaRegistro: datetime
    Activo: bool
    
    class Config:
        from_attributes = True


# =============================================
# SCHEMAS DE VENTAS
# =============================================

class DetalleVentaCreate(BaseModel):
    IdProducto: int = Field(..., gt=0)
    Cantidad: int = Field(..., gt=0)
    PrecioUnitario: Decimal = Field(..., gt=0)
    Descuento: Decimal = Field(0, ge=0)


class DetalleVentaOut(BaseModel):
    IdDetalleVenta: int
    IdProducto: int
    Cantidad: int
    PrecioUnitario: Decimal
    Descuento: Decimal
    SubTotal: Decimal
    
    class Config:
        from_attributes = True


class VentaCreate(BaseModel):
    IdCliente: Optional[int] = None
    IdUsuario: int = Field(..., gt=0)
    IdMetodoPago: int = Field(..., gt=0)
    Observaciones: Optional[str] = Field(None, max_length=500)
    detalles: List[DetalleVentaCreate] = Field(..., min_items=1)


class VentaOut(BaseModel):
    IdVenta: int
    NumeroVenta: str
    FechaVenta: datetime
    IdCliente: Optional[int]
    IdUsuario: int
    SubTotal: Decimal
    Descuento: Decimal
    Impuesto: Decimal
    Total: Decimal
    IdMetodoPago: int
    EstadoVenta: str
    detalles: List[DetalleVentaOut] = []
    
    class Config:
        from_attributes = True


# =============================================
# SCHEMAS DE IMÁGENES
# =============================================

class ImagenProductoOut(BaseModel):
    IdImagenProducto: int
    ImagenURL: str
    ImagenTipo: str
    ImagenNombre: str
    EsPrincipal: bool
    Orden: int
    FechaSubida: datetime
    
    class Config:
        from_attributes = True


class RespuestaImagen(BaseModel):
    mensaje: str
    url: str
    tipo: str


# =============================================
# SCHEMAS DE CONFIGURACIÓN
# =============================================

class ConfiguracionOut(BaseModel):
    IdConfig: int
    ClaveConfig: str
    ValorConfig: Optional[str]
    Descripcion: Optional[str]
    FechaActualizacion: datetime
    
    class Config:
        from_attributes = True