"""
helpers.py
Funciones utilitarias generales para el proyecto Jey2
Incluye manejo de fechas, validaciones, formateo y utilidades diversas
"""
from datetime import datetime, date, timedelta
from typing import Optional, Any, List, Dict, Union
from decimal import Decimal, InvalidOperation
import re
import unicodedata

# ==============================
# MANEJO DE FECHAS Y TIEMPO
# ==============================

def parsear_fecha(fecha_str: Optional[str], formato: str = "%Y-%m-%d") -> Optional[date]:
    """
    Convierte una cadena en un objeto date
    
    Args:
        fecha_str: Cadena de fecha
        formato: Formato de la fecha (por defecto YYYY-MM-DD)
        
    Returns:
        Objeto date o None si la entrada es None
        
    Raises:
        ValueError: Si el formato es inválido
    """
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str.strip(), formato).date()
    except ValueError:
        raise ValueError(
            f"Formato de fecha inválido: '{fecha_str}'. Esperado: {formato}"
        )


def parsear_datetime(
    fecha_str: Optional[str], 
    formato: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[datetime]:
    """
    Convierte una cadena en un objeto datetime
    """
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str.strip(), formato)
    except ValueError:
        raise ValueError(
            f"Formato de fecha/hora inválido: '{fecha_str}'. Esperado: {formato}"
        )


def formatear_fecha(
    fecha: Optional[Union[date, datetime]], 
    formato: str = "%Y-%m-%d"
) -> Optional[str]:
    """
    Formatea una fecha como string
    
    Args:
        fecha: Objeto date o datetime
        formato: Formato de salida
        
    Returns:
        String con fecha formateada o None
    """
    if not fecha:
        return None
    return fecha.strftime(formato)


def formatear_fecha_legible(fecha: Optional[Union[date, datetime]]) -> Optional[str]:
    """
    Formatea fecha en formato legible: "Lunes 25 de Diciembre, 2024"
    """
    if not fecha:
        return None
    
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    dias = [
        "Lunes", "Martes", "Miércoles", "Jueves", 
        "Viernes", "Sábado", "Domingo"
    ]
    
    dia_semana = dias[fecha.weekday()]
    mes = meses[fecha.month - 1]
    
    return f"{dia_semana} {fecha.day} de {mes}, {fecha.year}"


def dias_entre_fechas(fecha_inicio: date, fecha_fin: date) -> int:
    """
    Calcula la diferencia en días entre dos fechas
    """
    return (fecha_fin - fecha_inicio).days


def agregar_dias(fecha: date, dias: int) -> date:
    """
    Agrega o resta días a una fecha
    """
    return fecha + timedelta(days=dias)


def es_fecha_vencida(fecha_vencimiento: Optional[date]) -> bool:
    """
    Verifica si una fecha ya venció
    """
    if not fecha_vencimiento:
        return False
    return fecha_vencimiento < date.today()


def dias_para_vencer(fecha_vencimiento: Optional[date]) -> Optional[int]:
    """
    Calcula cuántos días faltan para que venza una fecha
    Retorna negativo si ya venció
    """
    if not fecha_vencimiento:
        return None
    return (fecha_vencimiento - date.today()).days


def obtener_rango_mes_actual() -> tuple[date, date]:
    """
    Retorna el primer y último día del mes actual
    """
    hoy = date.today()
    primer_dia = hoy.replace(day=1)
    
    # Último día del mes
    if hoy.month == 12:
        ultimo_dia = hoy.replace(day=31)
    else:
        siguiente_mes = hoy.replace(month=hoy.month + 1, day=1)
        ultimo_dia = siguiente_mes - timedelta(days=1)
    
    return primer_dia, ultimo_dia


# ==============================
# LIMPIEZA Y FORMATO DE TEXTO
# ==============================

def limpiar_texto(
    texto: Optional[str], 
    capitalizar: bool = True,
    eliminar_acentos: bool = False
) -> Optional[str]:
    """
    Limpia y formatea texto
    
    Args:
        texto: Texto a limpiar
        capitalizar: Si aplica title case
        eliminar_acentos: Si elimina acentos y diacríticos
        
    Returns:
        Texto limpio o None
    """
    if not texto:
        return None
    
    # Eliminar espacios extra
    texto = texto.strip()
    texto = re.sub(r"\s+", " ", texto)
    
    # Eliminar acentos si se solicita
    if eliminar_acentos:
        texto = eliminar_acentos_texto(texto)
    
    # Capitalizar
    if capitalizar:
        texto = texto.title()
    
    return texto


def eliminar_acentos_texto(texto: str) -> str:
    """
    Elimina acentos y diacríticos de un texto
    """
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


def normalizar_ruc(ruc: Optional[str]) -> Optional[str]:
    """
    Limpia y formatea el RUC (solo números y guiones)
    """
    if not ruc:
        return None
    return re.sub(r"[^0-9\-]", "", ruc.strip())


def normalizar_telefono(telefono: Optional[str]) -> Optional[str]:
    """
    Limpia y formatea número de teléfono
    """
    if not telefono:
        return None
    # Eliminar todo excepto números, guiones y paréntesis
    return re.sub(r"[^0-9\-\(\)\+\s]", "", telefono.strip())


def truncar_texto(texto: str, max_length: int, sufijo: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima
    """
    if len(texto) <= max_length:
        return texto
    return texto[:max_length - len(sufijo)] + sufijo


def slug_from_text(texto: str) -> str:
    """
    Genera un slug válido desde texto
    Ejemplo: "Arroz Premium 1kg" -> "arroz-premium-1kg"
    """
    texto = eliminar_acentos_texto(texto.lower())
    texto = re.sub(r'[^\w\s-]', '', texto)
    texto = re.sub(r'[\s_-]+', '-', texto)
    return texto.strip('-')


# ==============================
# VALIDACIONES
# ==============================

def validar_email(email: Optional[str]) -> bool:
    """
    Valida formato de email
    """
    if not email:
        return False
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email.strip()))


def validar_ruc_panama(ruc: Optional[str]) -> bool:
    """
    Valida formato de RUC panameño
    Formato básico: XX-XXX-XXXXX o variaciones
    """
    if not ruc:
        return False
    
    ruc = normalizar_ruc(ruc)
    # Patrón básico para RUC panameño
    patron = r'^\d{1,4}-\d{1,6}-\d{1,6}$|^\d{6,13}$'
    return bool(re.match(patron, ruc))


def validar_codigo_barras(codigo: Optional[str]) -> bool:
    """
    Valida que el código de barras tenga formato válido
    Acepta EAN-13, UPC-A, EAN-8, etc.
    """
    if not codigo:
        return False
    
    codigo = re.sub(r'\s', '', codigo)
    # Validar que solo contenga números y tenga longitud apropiada
    return bool(re.match(r'^\d{8}$|^\d{12,13}$', codigo))


def es_numero(valor: Any) -> bool:
    """
    Verifica si un valor puede convertirse a número
    """
    try:
        float(valor)
        return True
    except (TypeError, ValueError):
        return False


def validar_rango(
    valor: Union[int, float, Decimal], 
    minimo: Optional[Union[int, float, Decimal]] = None,
    maximo: Optional[Union[int, float, Decimal]] = None
) -> bool:
    """
    Valida que un valor esté dentro de un rango
    """
    if minimo is not None and valor < minimo:
        return False
    if maximo is not None and valor > maximo:
        return False
    return True


def validar_longitud_texto(
    texto: str, 
    minimo: int = 0, 
    maximo: Optional[int] = None
) -> bool:
    """
    Valida la longitud de un texto
    """
    longitud = len(texto)
    if longitud < minimo:
        return False
    if maximo is not None and longitud > maximo:
        return False
    return True


# ==============================
# FORMATEO DE DATOS
# ==============================

def formatear_moneda(
    valor: Union[int, float, Decimal], 
    simbolo: str = "B/.",
    decimales: int = 2
) -> str:
    """
    Formatea un número como moneda
    """
    try:
        return f"{simbolo} {float(valor):,.{decimales}f}"
    except (TypeError, ValueError):
        return f"{simbolo} 0.00"


def formatear_porcentaje(
    valor: Union[int, float, Decimal],
    decimales: int = 2
) -> str:
    """
    Formatea un número como porcentaje
    """
    try:
        return f"{float(valor):.{decimales}f}%"
    except (TypeError, ValueError):
        return "0.00%"


def formatear_numero(
    valor: Union[int, float, Decimal],
    decimales: int = 0,
    separador_miles: str = ","
) -> str:
    """
    Formatea un número con separador de miles
    """
    try:
        if decimales > 0:
            return f"{float(valor):,.{decimales}f}".replace(",", separador_miles)
        return f"{int(valor):,}".replace(",", separador_miles)
    except (TypeError, ValueError):
        return "0"


def generar_codigo(prefix: str, id: int, length: int = 6) -> str:
    """
    Genera códigos con formato PREFIX-000123
    """
    return f"{prefix.upper()}-{str(id).zfill(length)}"


def formatear_tamano_archivo(bytes: int) -> str:
    """
    Formatea tamaño de archivo en formato legible
    """
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


# ==============================
# CONVERSIONES
# ==============================

def string_to_decimal(valor: Any) -> Optional[Decimal]:
    """
    Convierte un string a Decimal de forma segura
    """
    if valor is None or valor == "":
        return None
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return None


def string_to_int(valor: Any, default: int = 0) -> int:
    """
    Convierte un string a int de forma segura
    """
    try:
        return int(valor)
    except (TypeError, ValueError):
        return default


def string_to_float(valor: Any, default: float = 0.0) -> float:
    """
    Convierte un string a float de forma segura
    """
    try:
        return float(valor)
    except (TypeError, ValueError):
        return default


def convertir_a_str(valor: Any) -> str:
    """
    Convierte cualquier valor a string de forma limpia
    """
    if valor is None:
        return ""
    if isinstance(valor, (int, float, Decimal)):
        return str(valor)
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return str(valor).strip()


def bool_to_str(valor: bool, si: str = "Sí", no: str = "No") -> str:
    """
    Convierte booleano a string personalizado
    """
    return si if valor else no


# ==============================
# UTILIDADES PARA LISTAS Y DICCIONARIOS
# ==============================

def safe_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Obtiene un atributo de forma segura
    """
    return getattr(obj, attr, default)


def obtener_valor_dict(
    diccionario: Dict, 
    clave: str, 
    default: Any = None,
    tipo: Optional[type] = None
) -> Any:
    """
    Obtiene un valor del diccionario con tipo opcional
    """
    valor = diccionario.get(clave, default)
    
    if tipo is not None and valor is not None:
        try:
            return tipo(valor)
        except (TypeError, ValueError):
            return default
    
    return valor


def dividir_lista(lista: List, tamano_chunk: int) -> List[List]:
    """
    Divide una lista en chunks de tamaño específico
    """
    return [lista[i:i + tamano_chunk] for i in range(0, len(lista), tamano_chunk)]


def aplanar_lista(lista_anidada: List[List]) -> List:
    """
    Aplana una lista de listas en una sola lista
    """
    return [item for sublista in lista_anidada for item in sublista]


def remover_duplicados(lista: List, mantener_orden: bool = True) -> List:
    """
    Elimina duplicados de una lista
    """
    if mantener_orden:
        return list(dict.fromkeys(lista))
    return list(set(lista))


# ==============================
# UTILIDADES DE NEGOCIO
# ==============================

def calcular_descuento(
    precio: Decimal, 
    porcentaje: Decimal
) -> Decimal:
    """
    Calcula el monto de descuento
    """
    return (precio * porcentaje) / Decimal('100')


def calcular_precio_con_descuento(
    precio: Decimal,
    porcentaje_descuento: Decimal
) -> Decimal:
    """
    Calcula precio final con descuento aplicado
    """
    descuento = calcular_descuento(precio, porcentaje_descuento)
    return precio - descuento


def calcular_impuesto(
    subtotal: Decimal,
    porcentaje_impuesto: Decimal
) -> Decimal:
    """
    Calcula el monto del impuesto
    """
    return (subtotal * porcentaje_impuesto) / Decimal('100')


def calcular_precio_con_impuesto(
    precio: Decimal,
    porcentaje_impuesto: Decimal
) -> Decimal:
    """
    Calcula precio final con impuesto incluido
    """
    impuesto = calcular_impuesto(precio, porcentaje_impuesto)
    return precio + impuesto


def calcular_margen_ganancia(
    precio_venta: Decimal,
    precio_compra: Decimal
) -> Decimal:
    """
    Calcula el margen de ganancia porcentual
    """
    if precio_compra == 0:
        return Decimal('0')
    return ((precio_venta - precio_compra) / precio_compra) * Decimal('100')


def redondear_decimal(valor: Decimal, decimales: int = 2) -> Decimal:
    """
    Redondea un Decimal a número específico de decimales
    """
    return valor.quantize(Decimal(10) ** -decimales)


# ==============================
# UTILIDADES DE SISTEMA
# ==============================

def es_produccion() -> bool:
    """
    Verifica si está en ambiente de producción
    """
    import os
    return os.getenv('ENV', 'development').lower() == 'production'


def obtener_ip_cliente(request) -> str:
    """
    Obtiene la IP del cliente desde el request
    """
    # Verificar si hay proxy
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


def generar_token_aleatorio(longitud: int = 32) -> str:
    """
    Genera un token aleatorio seguro
    """
    import secrets
    return secrets.token_urlsafe(longitud)


# ==============================
# UTILIDADES DE LOGGING
# ==============================

def log_accion(usuario_id: int, accion: str, detalles: str = "") -> None:
    """
    Registra una acción en el log (placeholder)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"[{timestamp}] Usuario {usuario_id}: {accion}"
    if detalles:
        mensaje += f" - {detalles}"
    print(mensaje)  # En producción, usar logging real