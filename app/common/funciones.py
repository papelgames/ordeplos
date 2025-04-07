from app.models import Estados
from flask_login import current_user

def listar_endpoints(app):
    """
    Lista todos los endpoints registrados en la aplicación Flask.
    """
    endpoints = []

    for rule in app.url_map.iter_rules():
        endpoints.append({'descripcion' :rule.endpoint, 
                            'usuario_alta':current_user.username})
    return endpoints

def generar_cuil_cuit(dni: int, genero: str) -> str:
    """
    Genera un número de CUIL/CUIT argentino basado en el DNI y el género.
    
    Args:
        dni (int): Número de documento (sin puntos).
        genero (str): 'M' para masculino, 'F' para femenino, 'X' para no binario, 'E' para empresa.

    Returns:
        str: Número de CUIL/CUIT en formato XX-DNI-Y
    """
    
    # Prefijo según el género
    prefijos = {'M': 20, 'F': 27, 'X': 30, 'E': 30}  # Empresas y no binario usan 30
    prefijo = prefijos.get(genero.upper(), 30)  # Si el género no es válido, usa 30 por defecto

    # Convertir en string con ceros a la izquierda si es necesario
    dni_str = str(dni).zfill(8)
    
    # Calcular el dígito verificador
    base = f"{prefijo}{dni_str}00"
    multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = sum(int(base[i]) * multiplicadores[i] for i in range(10))
    
    resto = suma % 11
    verificador = 11 - resto

    # Ajustes especiales si el resultado es 10 u 11
    if verificador == 10:
        verificador = 9 if prefijo == 20 else 4
    elif verificador == 11:
        verificador = 0

    return f"{prefijo}{dni_str}{verificador}"

