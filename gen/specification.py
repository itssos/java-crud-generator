import os
import re
import inquirer

def extraer_atributos_search(codigo_java):
    """
    Extrae los atributos de la clase SearchModel Java.
    Busca variables privadas con su tipo de dato y nombre.
    """
    return re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)

def seleccionar_atributos(atributos):
    """
    Permite seleccionar qué atributos incluir en Specifications mediante consola.
    """
    if not atributos:
        return []
    
    preguntas = [
        inquirer.Checkbox(
            "atributos",
            message="Seleccione los atributos para Specifications (Presione ESPACIO y ENTER para confirmar):",
            choices=[f"{tipo} {nombre}" for tipo, nombre in atributos],
        )
    ]
    respuestas = inquirer.prompt(preguntas)

    if respuestas and "atributos" in respuestas:
        return [tuple(attr.split(" ")) for attr in respuestas["atributos"]]
    
    return []

def generar_specifications(nombre_entidad, paquete, atributos_seleccionados):
    """
    Genera el código Java para Specifications con los atributos seleccionados desde SearchModel.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_spec = f"{nombre_simple}Specifications"

    # Importaciones necesarias
    importaciones = f"""package {paquete}.specifications;

import {paquete}.models.entities.{nombre_entidad};
import lombok.experimental.UtilityClass;
import org.springframework.data.jpa.domain.Specification;
"""

    # Método vacío `empty()`
    metodo_empty = f"""
@UtilityClass
public class {nombre_spec} {{

    public static Specification<{nombre_entidad}> empty() {{
        return (root, query, builder) -> builder.conjunction();
    }}
"""

    # Métodos para cada atributo seleccionado
    especificaciones = "\n".join([
        f"""    public static Specification<{nombre_entidad}> {attr}(final {tipo} {attr}) {{
        return (root, query, builder) -> builder.equal(root.get("{attr}"), {attr});
    }}"""
        for tipo, attr in atributos_seleccionados
    ])

    # Cerrar la clase
    cierre_clase = "}\n"

    # Generar código completo
    specifications_code = f"""{importaciones}
{metodo_empty}
{especificaciones}
{cierre_clase}
"""
    return nombre_spec, specifications_code  # Devolver el nombre correcto y el código generado

def generar_specifications_archivo(entidad_file):
    """
    Lee el archivo de la entidad y genera Specifications en la carpeta 'specifications/'.
    """
    # Obtener el nombre de la entidad sin ".java"
    nombre_entidad = os.path.basename(entidad_file).replace(".java", "")
    nombre_simple = nombre_entidad.replace("Entity", "")

    # Definir el archivo SearchModel generado previamente
    search_file = os.path.join("search", f"{nombre_simple}SearchModel.java")

    if not os.path.exists(search_file):
        print(f"❌ No se encontró el archivo SearchModel: {search_file}")
        return ""

    # Leer código Java del SearchModel
    with open(search_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer metadatos
    paquete = extraer_paquete(codigo_java)
    atributos = extraer_atributos_search(codigo_java)

    if not nombre_entidad or not atributos:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos del SearchModel.")
        return ""

    # ✅ Permitir selección de atributos por consola
    atributos_seleccionados = seleccionar_atributos(atributos)

    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. No se generará Specifications.")
        return ""

    # Generar Specifications
    nombre_spec, spec_code = generar_specifications(nombre_entidad, paquete, atributos_seleccionados)

    # ✅ Crear carpeta `specifications/` en la raíz si no existe
    os.makedirs("specifications", exist_ok=True)

    # ✅ Guardar archivo en `specifications/`
    spec_file = os.path.join("specifications", f"{nombre_spec}.java")
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_code)

    print(f"✅ Specifications generado en: {spec_file}")

    return spec_code  # Retorna el código generado para evitar None

# Función auxiliar para extraer el paquete
def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"

