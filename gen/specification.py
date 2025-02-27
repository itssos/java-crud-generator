import os
import re
import inquirer

def extraer_atributos_entidad(codigo_java):
    """
    Extrae los atributos de la clase Entity en Java.
    Busca variables privadas con su tipo de dato y nombre.
    """
    patron = re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)
    return patron

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

def generar_specifications(nombre_entidad, paquete_entidad, atributos_seleccionados):
    """
    Genera el código Java para Specifications con los atributos seleccionados.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_spec = f"{nombre_simple}Specifications"

    # El package se fija siempre
    paquete_specifications = "com.inycom.cws.specifications"

    # Importaciones (incluye el Entity original)
    importaciones = f"""package {paquete_specifications};

import {paquete_entidad}.{nombre_entidad};
import lombok.experimental.UtilityClass;
import org.springframework.data.jpa.domain.Specification;
"""

    # Método empty()
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

    cierre_clase = "}\n"

    specifications_code = f"""{importaciones}
{metodo_empty}
{especificaciones}
{cierre_clase}
"""
    return nombre_spec, specifications_code

def generar_specifications_archivo(entidad_file, atributos_seleccionados=None):
    """
    Genera Specifications a partir del archivo de la entidad.
    Si se pasa una lista de atributos ya seleccionados, se usa esa; de lo contrario, se extrae y solicita.
    """
    nombre_entidad = os.path.basename(entidad_file).replace(".java", "")

    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    paquete = extraer_paquete(codigo_java)
    atributos = extraer_atributos_entidad(codigo_java)

    if not nombre_entidad or not atributos:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos.")
        return ""

    if atributos_seleccionados is None:
        atributos_seleccionados = seleccionar_atributos(atributos)

    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. No se generará Specifications.")
        return ""

    nombre_spec, spec_code = generar_specifications(nombre_entidad, paquete, atributos_seleccionados)

    os.makedirs("specifications", exist_ok=True)

    spec_file = os.path.join("specifications", f"{nombre_spec}.java")
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_code)

    print(f"✅ Specifications generado en: {spec_file}")
    return spec_code

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
