"""
Punto de entrada principal de la aplicación FastAPI
Sistema Jey2 - Abarrotería, Carnicería y Bodega Elda
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_connection, init_db
import os

# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema Jey2 API",
    description="API para gestión de Abarrotería, Carnicería y Bodega Elda",
    version="1.0.0",
    docs_url="/docs",  # Documentación Swagger
    redoc_url="/redoc"  # Documentación ReDoc
)

# Configurar CORS para permitir peticiones desde el frontend Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (Vue)
        "http://localhost:3000",  # Alternativa
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

# Montar carpeta de archivos estáticos (imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# =============================================
# IMPORTAR Y REGISTRAR ROUTERS
# =============================================

from app.routers import auth, productos, usuarios, proveedores, imagenes

# Registrar routers con prefijos
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(productos.router, prefix="/api/productos", tags=["Productos"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(proveedores.router, prefix="/api/proveedores", tags=["Proveedores"])
app.include_router(imagenes.router, prefix="/api/imagenes", tags=["Imágenes"])

# =============================================
# EVENTOS DE INICIO Y CIERRE
# =============================================

@app.on_event("startup")
async def startup_event():
    """
    Se ejecuta al iniciar la aplicación
    """
    print("=" * 50)
    print("Iniciando Sistema Jey2 API...")
    print("=" * 50)
    
    # Verificar conexión a la base de datos
    if test_connection():
        print("Base de datos conectada correctamente")
    else:
        print("Advertencia: No se pudo conectar a la base de datos")
    
    # Inicializar base de datos (crear tablas si no existen)
    init_db()
    
    # Crear carpetas para imágenes si no existen
    os.makedirs("static/imagenes/productos", exist_ok=True)
    os.makedirs("static/imagenes/usuarios", exist_ok=True)
    os.makedirs("static/imagenes/proveedores", exist_ok=True)
    print("Carpetas de imágenes verificadas")
    
    print("=" * 50)
    print("istema Jey2 API iniciado correctamente")
    print("Documentación disponible en: http://localhost:8000/docs")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Se ejecuta al cerrar la aplicación
    """
    print("=" * 50)
    print("Cerrando Sistema Jey2 API...")
    print("=" * 50)

# =============================================
# RUTAS BÁSICAS
# =============================================

@app.get("/")
async def root():
    """
    Ruta raíz - Información de la API
    """
    return {
        "mensaje": "Sistema Jey2 API",
        "version": "1.0.0",
        "empresa": "Abarrotería, Carnicería y Bodega Elda",
        "documentacion": "/docs",
        "estado": "activo"
    }


@app.get("/health")
async def health_check():
    """
    Verificar el estado de salud de la API
    """
    db_status = test_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "api_version": "1.0.0"
    }


# =============================================
# MANEJO DE ERRORES GLOBAL
# =============================================

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Manejo global de errores de base de datos
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error en la base de datos",
            "error": str(exc)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejo global de errores generales
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc)
        }
    )


# =============================================
# EJECUTAR LA APLICACIÓN
# =============================================

if __name__ == "__main__":
    import uvicorn
    
    # Obtener configuración desde variables de entorno
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Ejecutar servidor
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True,  # Activar recarga automática en desarrollo
        log_level="info"
    )