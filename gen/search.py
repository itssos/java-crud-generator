import os
import re
import inquirer

def extraer_atributos(codigo_java):
    """
    Extrae los atributos de la clase Java.
    Busca variables privadas con su tipo de dato y nombre.
    """
    patron = re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)
    return patron

def seleccionar_atributos(atributos):
    """
    Permite seleccionar atributos usando un menú interactivo en consola con `inquirer`.
    """
    preguntas = [
        inquirer.Checkbox(
            "atributos",
            message="Seleccione los atributos que desea incluir en el SearchModel, Specification y Factories:",
            choices=[f"{tipo} {nombre}" for tipo, nombre in atributos],
        )
    ]
    respuestas = inquirer.prompt(preguntas)
    
    if respuestas and "atributos" in respuestas:
        return [tuple(attr.split(" ")) for attr in respuestas["atributos"]]
    
    return []

def generar_search_model(nombre_entidad, paquete, atributos_seleccionados):
    """
    Genera el código Java para el SearchModel con los atributos seleccionados.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_search = f"{nombre_simple}SearchModel"

    # Importaciones necesarias
    importaciones = """import lombok.Data;
"""

    # Fijamos el package de forma fija (igual que en Specifications)
    paquete_search = "com.inycom.cws.search"

    # Definir los atributos del SearchModel
    atributos_str = "\n    ".join([f"private {tipo} {nombre};" for tipo, nombre in atributos_seleccionados])

    # Generar código del SearchModel
    search_code = f"""package {paquete_search};

{importaciones}

@Data
public class {nombre_search} {{

    {atributos_str}
}}
"""
    return search_code

def generar_search_model_archivo(entidad_file, atributos_seleccionados=None):
    """
    Genera el SearchModel correspondiente a partir del archivo de la entidad.
    Si se pasa una lista de atributos ya seleccionados, se usa esa; de lo contrario, se extrae y solicita.
    """
    # Leer código Java
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer metadatos
    nombre_entidad = extraer_nombre_entidad(codigo_java)
    paquete = extraer_paquete(codigo_java)
    atributos = extraer_atributos(codigo_java)

    if not nombre_entidad or not atributos:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos.")
        return

    # Si no se han pasado atributos seleccionados, se solicita por consola
    if atributos_seleccionados is None:
        atributos_seleccionados = seleccionar_atributos(atributos)

    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. No se generará el SearchModel.")
        return

    # Generar SearchModel
    search_code = generar_search_model(nombre_entidad, paquete, atributos_seleccionados)

    # Crear carpeta 'output/search' si no existe
    search_dir = os.path.join("output", "search")
    os.makedirs(search_dir, exist_ok=True)

    # Guardar archivo en 'output/search' con el nombre adecuado
    search_file = os.path.join(search_dir, f"{nombre_entidad.replace('Entity', '')}SearchModel.java")
    with open(search_file, "w", encoding="utf-8") as f:
        f.write(search_code)

    print(f"✅ SearchModel generado en: {search_file}")

# Funciones auxiliares para extraer nombre de entidad y paquete
def extraer_nombre_entidad(codigo_java):
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
