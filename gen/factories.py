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
    Permite seleccionar qué atributos incluir en la Specification Factory mediante consola.
    """
    if not atributos:
        return []
    
    preguntas = [
        inquirer.Checkbox(
            "atributos",
            message="Seleccione los atributos para la Specification Factory (Presione ESPACIO y ENTER para confirmar):",
            choices=[f"{tipo} {nombre}" for tipo, nombre in atributos],
        )
    ]
    respuestas = inquirer.prompt(preguntas)
    if respuestas and "atributos" in respuestas:
        return [tuple(attr.split(" ")) for attr in respuestas["atributos"]]
    return []

def generar_factories_specifications(nombre_entidad, paquete, atributos_seleccionados):
    """
    Genera el código Java para las Specifications que serán usadas en la Specification Factory,
    con los atributos seleccionados desde el SearchModel.
    Se utiliza un package fijo: "com.inycom.cws.specifications".
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_spec = f"{nombre_simple}Specifications"

    # Usamos un package fijo para specifications
    importaciones = """package com.inycom.cws.specifications;

import com.inycom.cws.models.entities.""" + f"{nombre_entidad};\n" + \
"""import lombok.experimental.UtilityClass;
import org.springframework.data.jpa.domain.Specification;
"""

    metodo_empty = f"""
@UtilityClass
public class {nombre_spec} {{

    public static Specification<{nombre_entidad}> empty() {{
        return (root, query, builder) -> builder.conjunction();
    }}
"""

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

def generar_factories_factory(nombre_entidad, paquete, atributos_seleccionados):
    """
    Genera el código Java para la Specification Factory con los atributos seleccionados desde el SearchModel.
    Se utiliza un package fijo: "com.inycom.cws.factories".
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_search = f"{nombre_simple}SearchModel"
    nombre_spec = f"{nombre_simple}Specifications"
    nombre_factory = f"{nombre_simple}SpecificationFactory"

    # Usamos un package fijo para factories
    importaciones = f"""package com.inycom.cws.factories;

import com.inycom.cws.models.entities.{nombre_entidad};
import com.inycom.cws.search.{nombre_search};
import com.inycom.cws.specifications.{nombre_spec};
import lombok.experimental.UtilityClass;
import org.springframework.data.jpa.domain.Specification;

import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
"""

    especificaciones = "\n".join([
        f"""        Optional.ofNullable(searchModel.get{attr.capitalize()}())
                .map({nombre_spec}::{attr})
                .ifPresent(specifications::add);"""
        for _, attr in atributos_seleccionados
    ])

    factory_code = f"""{importaciones}

@UtilityClass
public class {nombre_factory} {{

    public Specification<{nombre_entidad}> mapToSpecification(final {nombre_search} searchModel) {{

        final List<Specification<{nombre_entidad}>> specifications = new LinkedList<>();

{especificaciones}

        return specifications.stream()
                .reduce(Specification::and)
                .orElse({nombre_spec}.empty());
    }}
}}
"""
    return nombre_factory, factory_code

def generar_archivos_factories(entidad_file, atributos_seleccionados):
    """
    Genera tanto las Specifications como la Specification Factory a partir del archivo de la entidad
    y de la lista de atributos seleccionados (ya realizada).
    Se asume que la lista de atributos ya fue seleccionada previamente.
    """
    # Obtener el nombre de la entidad sin la extensión ".java"
    nombre_entidad = os.path.basename(entidad_file).replace(".java", "")
    nombre_simple = nombre_entidad.replace("Entity", "")

    # Definir el archivo SearchModel generado previamente
    search_file = os.path.join("search", f"{nombre_simple}SearchModel.java")
    if not os.path.exists(search_file):
        print(f"❌ No se encontró el archivo SearchModel: {search_file}")
        return ""

    # Leer el código Java del SearchModel
    with open(search_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer el package del SearchModel (aunque se usará un package fijo para factories)
    paquete_extraido = extraer_paquete(codigo_java)
    # Validar que se extrajeron atributos del SearchModel
    atributos_search = extraer_atributos_search(codigo_java)
    if not nombre_entidad or not atributos_search:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos del SearchModel.")
        return ""

    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. No se generarán las Specifications ni la Specification Factory.")
        return ""

    # Generar Specifications (para la fábrica) y Specification Factory usando los mismos atributos
    nombre_spec, spec_code = generar_factories_specifications(nombre_entidad, None, atributos_seleccionados)
    nombre_factory, factory_code = generar_factories_factory(nombre_entidad, None, atributos_seleccionados)

    # Crear carpetas si no existen
    os.makedirs("specifications", exist_ok=True)
    os.makedirs("factories", exist_ok=True)

    # Guardar archivos
    spec_file = os.path.join("specifications", f"{nombre_spec}.java")
    factory_file = os.path.join("factories", f"{nombre_factory}.java")
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_code)
    with open(factory_file, "w", encoding="utf-8") as f:
        f.write(factory_code)

    print(f"✅ Specifications generado en: {spec_file}")
    print(f"✅ SpecificationFactory generado en: {factory_file}")

    return spec_code, factory_code

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
