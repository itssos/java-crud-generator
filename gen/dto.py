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
            message="Seleccione los atributos que desea incluir en el DTO (Presione ESPACIO para seleccionar y ENTER para confirmar):",
            choices=[f"{tipo} {nombre}" for tipo, nombre in atributos],
        )
    ]
    respuestas = inquirer.prompt(preguntas)
    
    if respuestas and "atributos" in respuestas:
        return [tuple(attr.split(" ")) for attr in respuestas["atributos"]]
    
    return []

def generar_dto(nombre_entidad, paquete, atributos_seleccionados):
    """
    Genera el código Java para el DTO con los atributos seleccionados.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_dto = f"{nombre_simple}Dto"

    # Importaciones necesarias
    importaciones = """import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;
import jakarta.persistence.Embeddable;
"""

    # Definir los atributos del DTO
    atributos_str = "\n    ".join([f"private {tipo} {nombre};" for tipo, nombre in atributos_seleccionados])

    # Generar código del DTO
    dto_code = f"""package {paquete}.models.dtos;

{importaciones}

@SuperBuilder(toBuilder = true)
@Data
@AllArgsConstructor
@NoArgsConstructor
@Embeddable
public class {nombre_dto} {{

    {atributos_str}
}}
"""
    return dto_code

def generar_dto_archivo(entidad_file):
    """
    Lee el archivo de la entidad y genera el DTO correspondiente.
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

    # Permitir selección de atributos con menú interactivo
    atributos_seleccionados = seleccionar_atributos(atributos)

    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. No se generará el DTO.")
        return

    # Generar DTO
    dto_code = generar_dto(nombre_entidad, paquete, atributos_seleccionados)

    # Crear carpeta si no existe
    os.makedirs("models/dtos", exist_ok=True)

    # Guardar archivo
    dto_file = os.path.join("models/dtos", f"{nombre_entidad.replace('Entity', '')}Dto.java")
    with open(dto_file, "w", encoding="utf-8") as f:
        f.write(dto_code)

    print(f"✅ DTO generado: {dto_file}")

# Funciones auxiliares para extraer nombre de entidad y paquete
def extraer_nombre_entidad(codigo_java):
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"

# Si se ejecuta directamente, probar la generación
if __name__ == "__main__":
    entidad_file = "C:\\Users\\diego\\OneDrive\\Documentos\\Github\\java-crud-generator\\prueba.java"
    generar_dto_archivo(entidad_file)
