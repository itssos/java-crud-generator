import re
def extraer_nombre_entidad(codigo_java):
    """
    Busca la clase que contenga 'public class' y retorna el nombre.
    Por ejemplo, 'PatientEntity'.
    """
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def extraer_paquete(codigo_java):
    """
    Busca la línea 'package com.xxx.yyy;' para extraer el nombre del paquete.
    """
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"