"""
Configuración de conexión a SQL Server usando SQLAlchemy
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import urllib.parse

# Cargar variables de entorno
load_dotenv()

# Obtener credenciales desde .env
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "Jey2DB")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Construir connection string para SQL Server
# Formato: mssql+pyodbc://usuario:contraseña@servidor/base_datos?driver=ODBC+Driver+17+for+SQL+Server
params = urllib.parse.quote_plus(
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    "TrustServerCertificate=yes;"
)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Crear engine de SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Cambiar a True para ver queries SQL en consola (útil para debug)
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=10,  # Número de conexiones en el pool
    max_overflow=20,  # Conexiones adicionales si se necesitan
)

# Configurar opciones de sesión para SQL Server
@event.listens_for(engine, "connect")
def set_connection_options(dbapi_conn, connection_record):
    """Configurar opciones de conexión específicas de SQL Server"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET NOCOUNT ON")
    cursor.execute("SET ARITHABORT ON")
    cursor.close()

# Crear SessionLocal para manejar sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener sesión de BD
def get_db():
    """
    Generador de sesiones de base de datos.
    Uso en FastAPI:
        @app.get("/usuarios/")
        def read_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar conexión
def test_connection():
    """
    Verifica que la conexión a la base de datos funcione correctamente
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT @@VERSION"))
            version = result.fetchone()
            print("✅ Conexión exitosa a SQL Server")
            print(f"📊 Versión: {version[0][:50]}...")
            return True
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return False

# Función para inicializar la base de datos
def init_db():
    """
    Crea todas las tablas en la base de datos (si no existen)
    NOTA: Como tu BD ya existe, esto solo verificará las tablas
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos verificada/inicializada")
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")