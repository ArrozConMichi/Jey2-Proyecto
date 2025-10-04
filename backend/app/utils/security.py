"""
Utilidades de seguridad: Hash de contraseñas y JWT
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Configuración de JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_cambiar_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================
# FUNCIONES DE HASH DE CONTRASEÑAS
# =============================================

def hash_password(password: str) -> bytes:
    """
    Genera el hash de una contraseña
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña en bytes (para guardar en VARBINARY)
    """
    hashed = pwd_context.hash(password)
    return hashed.encode('utf-8')


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado (VARBINARY de SQL Server)
        
    Returns:
        True si la contraseña es correcta, False si no
    """
    try:
        # Convertir bytes a string
        hashed_str = hashed_password.decode('utf-8')
        return pwd_context.verify(plain_password, hashed_str)
    except Exception as e:
        print(f"Error al verificar contraseña: {e}")
        return False


# =============================================
# FUNCIONES DE JWT (JSON Web Tokens)
# =============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT
    
    Args:
        data: Datos a incluir en el token (username, id_usuario, etc.)
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Codificar token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y verifica un token JWT
    
    Args:
        token: Token JWT como string
        
    Returns:
        Datos del token si es válido, None si no
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Error al decodificar token: {e}")
        return None


# =============================================
# VALIDACIÓN DE CONTRASEÑAS
# =============================================

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida la fortaleza de una contraseña
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_valida, mensaje)
    """
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 100:
        return False, "La contraseña no puede exceder 100 caracteres"
    
    # Verificar que contenga al menos una letra y un número (opcional)
    tiene_letra = any(c.isalpha() for c in password)
    tiene_numero = any(c.isdigit() for c in password)
    
    if not (tiene_letra and tiene_numero):
        return False, "La contraseña debe contener letras y números"
    
    return True, "Contraseña válida"


# =============================================
# GENERADOR DE CONTRASEÑAS TEMPORALES
# =============================================

import secrets
import string

def generate_temp_password(length: int = 10) -> str:
    """
    Genera una contraseña temporal segura
    
    Args:
        length: Longitud de la contraseña
        
    Returns:
        Contraseña temporal
    """
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password