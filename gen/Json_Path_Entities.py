import os
import re
import json
import inquirer

def listar_entidades(directorio):
    """
    Lista todos los archivos de entidades dentro del directorio especificado.
    """
    return [f for f in os.listdir(directorio) if f.endswith("Entity.java")]

def extraer_atributos(codigo_java):
    """
    Extrae los atributos de la entidad eliminando anotaciones de JPA.
    """
    atributos = []
    for linea in codigo_java.splitlines():
        linea = linea.strip()
        if linea.startswith("private "):
            tipo_nombre = linea.replace("private ", "").replace(";", "").split(" ")
            if len(tipo_nombre) == 2:
                tipo, nombre = tipo_nombre
                atributos.append({"type": tipo, "name": nombre})
    return atributos

def seleccionar_entidad(entidades):
    """
    Permite seleccionar una entidad desde la consola.
    """
    preguntas = [
        inquirer.List("entidad", message="Selecciona una entidad", choices=entidades)
    ]
    respuestas = inquirer.prompt(preguntas)
    return respuestas["entidad"] if respuestas else None

def leer_codigo_entidad(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        return f.read()

def extraer_nombre_entidad(codigo_java):
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def generar_json_entidad(entidad, atributos, salida_dir="output"):
    """
    Genera un archivo JSON con la estructura de la entidad.
    """
    os.makedirs(salida_dir, exist_ok=True)
    archivo_salida = os.path.join(salida_dir, f"{entidad}.json")
    
    data = {
        "name": entidad,
        "attributes": atributos
    }
    
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Archivo JSON generado: {archivo_salida}")

def main():
    directorio_entidades = input("📂 Ingrese la ruta de la carpeta de entidades: ")
    if not os.path.exists(directorio_entidades):
        print("❌ Error: El directorio no existe.")
        return
    
    entidades = listar_entidades(directorio_entidades)
    if not entidades:
        print("❌ No se encontraron entidades en el directorio.")
        return

    entidad_seleccionada = seleccionar_entidad(entidades)
    if not entidad_seleccionada:
        print("⚠ No se seleccionó ninguna entidad.")
        return

    ruta_entidad = os.path.join(directorio_entidades, entidad_seleccionada)
    codigo_java = leer_codigo_entidad(ruta_entidad)
    nombre_entidad = extraer_nombre_entidad(codigo_java)
    atributos = extraer_atributos(codigo_java)

    if not nombre_entidad or not atributos:
        print("❌ No se pudo extraer información de la entidad.")
        return
    
    generar_json_entidad(nombre_entidad, atributos)

if __name__ == "__main__":
    main()
