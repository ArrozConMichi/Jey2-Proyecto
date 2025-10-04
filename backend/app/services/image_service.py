"""
Servicio para manejo de imágenes (productos, usuarios, proveedores)
"""
import os
import shutil
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image
import secrets
from pathlib import Path

# Configuración
UPLOAD_DIR = "static/imagenes"
MAX_SIZE_MB = 5
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_DIMENSION = 2048  # Redimensionar si es mayor

# =============================================
# VALIDACIÓN DE IMÁGENES
# =============================================

def validar_extension(filename: str) -> bool:
    """
    Valida que la extensión del archivo sea permitida
    """
    extension = filename.split('.')[-1].lower()
    return extension in ALLOWED_EXTENSIONS


def validar_tamano(file: UploadFile) -> bool:
    """
    Valida que el tamaño del archivo no exceda el máximo
    """
    # Obtener tamaño del archivo
    file.file.seek(0, 2)  # Ir al final del archivo
    size = file.file.tell()
    file.file.seek(0)  # Volver al inicio
    
    return size <= MAX_SIZE_BYTES


def obtener_extension(filename: str) -> str:
    """
    Obtiene la extensión del archivo
    """
    return filename.split('.')[-1].lower()


# =============================================
# PROCESAMIENTO DE IMÁGENES
# =============================================

def generar_nombre_unico(extension: str) -> str:
    """
    Genera un nombre único para el archivo
    """
    return f"{secrets.token_urlsafe(16)}.{extension}"


def optimizar_imagen(ruta_imagen: str) -> None:
    """
    Optimiza una imagen: redimensiona si es muy grande y comprime
    """
    try:
        with Image.open(ruta_imagen) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensionar si es muy grande
            if img.width > MAX_IMAGE_DIMENSION or img.height > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
            
            # Guardar con compresión
            img.save(ruta_imagen, optimize=True, quality=85)
    
    except Exception as e:
        print(f"Error al optimizar imagen: {e}")
        # Si falla la optimización, continuar sin optimizar


# =============================================
# GUARDAR IMÁGENES
# =============================================

async def guardar_imagen(
    file: UploadFile,
    tipo: str,  # 'productos', 'usuarios', 'proveedores'
    id_entidad: Optional[int] = None
) -> Tuple[str, str]:
    """
    Guarda una imagen y retorna la URL y el tipo
    
    Args:
        file: Archivo subido
        tipo: Tipo de entidad (productos, usuarios, proveedores)
        id_entidad: ID de la entidad (opcional, para nombrar el archivo)
    
    Returns:
        Tupla (url_relativa, extension)
    
    Raises:
        HTTPException: Si hay error en validación o guardado
    """
    # Validar extensión
    if not validar_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar tamaño
    if not validar_tamano(file):
        raise HTTPException(
            status_code=400,
            detail=f"El archivo excede el tamaño máximo de {MAX_SIZE_MB}MB"
        )
    
    # Crear directorio si no existe
    directorio = os.path.join(UPLOAD_DIR, tipo)
    os.makedirs(directorio, exist_ok=True)
    
    # Generar nombre único o usar ID de entidad
    extension = obtener_extension(file.filename)
    if id_entidad:
        nombre_archivo = f"{id_entidad}_{secrets.token_urlsafe(8)}.{extension}"
    else:
        nombre_archivo = generar_nombre_unico(extension)
    
    # Ruta completa
    ruta_completa = os.path.join(directorio, nombre_archivo)
    
    try:
        # Guardar archivo
        with open(ruta_completa, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Optimizar imagen
        optimizar_imagen(ruta_completa)
        
        # URL relativa para la base de datos
        url_relativa = f"/static/imagenes/{tipo}/{nombre_archivo}"
        
        return url_relativa, extension
    
    except Exception as e:
        # Eliminar archivo si hubo error
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar la imagen: {str(e)}"
        )


# =============================================
# ELIMINAR IMÁGENES
# =============================================

def eliminar_imagen(url_imagen: str) -> bool:
    """
    Elimina una imagen del sistema de archivos
    
    Args:
        url_imagen: URL relativa de la imagen (ej: /static/imagenes/productos/abc.jpg)
    
    Returns:
        True si se eliminó correctamente, False si no
    """
    try:
        # Convertir URL relativa a ruta del sistema
        if url_imagen.startswith('/static/'):
            ruta = url_imagen.replace('/static/', '', 1)
        else:
            ruta = url_imagen
        
        ruta_completa = os.path.join('static', ruta) if not ruta.startswith('static') else ruta
        
        # Eliminar archivo
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
            return True
        else:
            print(f"Archivo no encontrado: {ruta_completa}")
            return False
    
    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
        return False


# =============================================
# REEMPLAZAR IMAGEN
# =============================================

async def reemplazar_imagen(
    file: UploadFile,
    url_imagen_anterior: Optional[str],
    tipo: str,
    id_entidad: Optional[int] = None
) -> Tuple[str, str]:
    """
    Reemplaza una imagen existente por una nueva
    
    Args:
        file: Nueva imagen
        url_imagen_anterior: URL de la imagen a reemplazar (puede ser None)
        tipo: Tipo de entidad
        id_entidad: ID de la entidad
    
    Returns:
        Tupla (url_relativa, extension)
    """
    # Guardar nueva imagen
    nueva_url, extension = await guardar_imagen(file, tipo, id_entidad)
    
    # Eliminar imagen anterior si existe
    if url_imagen_anterior:
        eliminar_imagen(url_imagen_anterior)
    
    return nueva_url, extension


# =============================================
# VERIFICAR EXISTENCIA
# =============================================

def imagen_existe(url_imagen: str) -> bool:
    """
    Verifica si una imagen existe en el sistema de archivos
    """
    if not url_imagen:
        return False
    
    ruta = url_imagen.replace('/static/', '', 1)
    ruta_completa = os.path.join('static', ruta)
    
    return os.path.exists(ruta_completa)


# =============================================
# OBTENER INFORMACIÓN DE IMAGEN
# =============================================

def obtener_info_imagen(ruta_imagen: str) -> dict:
    """
    Obtiene información de una imagen
    """
    try:
        if not os.path.exists(ruta_imagen):
            return None
        
        with Image.open(ruta_imagen) as img:
            return {
                "formato": img.format,
                "modo": img.mode,
                "ancho": img.width,
                "alto": img.height,
                "tamano_bytes": os.path.getsize(ruta_imagen)
            }
    except Exception as e:
        print(f"Error al obtener info de imagen: {e}")
        return None