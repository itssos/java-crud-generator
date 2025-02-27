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
    return nombre_spec, specifications_code, atributos_seleccionados  # También devuelve los atributos seleccionados

def generar_specification_factory(nombre_entidad, paquete, atributos_seleccionados):
    """
    Genera el código Java para la SpecificationFactory con los atributos seleccionados desde SearchModel.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_search = f"{nombre_simple}SearchModel"
    nombre_spec = f"{nombre_simple}Specifications"
    nombre_factory = f"{nombre_simple}SpecificationFactory"

    # Importaciones necesarias
    importaciones = f"""package {paquete}.factories;

import {paquete}.models.entities.{nombre_entidad};
import {paquete}.search.{nombre_search};
import {paquete}.specifications.{nombre_spec};
import lombok.experimental.UtilityClass;
import org.springframework.data.jpa.domain.Specification;

import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
"""

    # Construcción de la lista de especificaciones basada en los atributos seleccionados
    especificaciones = "\n".join([
        f"""        Optional.ofNullable(searchModel.get{attr.capitalize()}())
                .map({nombre_spec}::{attr})
                .ifPresent(specifications::add);"""
        for _, attr in atributos_seleccionados
    ])

    # Generar código del SpecificationFactory
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
    return nombre_factory, factory_code  # Devuelve también el nombre correcto de la clase

def generar_archivos_specifications_y_factory(entidad_file):
    """
    Lee el archivo de la entidad y genera tanto Specifications como SpecificationFactory,
    asegurando que ambos usen los mismos atributos seleccionados.
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
        print("⚠ No se seleccionaron atributos. No se generará Specifications ni SpecificationFactory.")
        return ""

    # Generar Specifications
    nombre_spec, spec_code, atributos_usados = generar_specifications(nombre_entidad, paquete, atributos_seleccionados)

    # Generar SpecificationFactory usando los mismos atributos
    nombre_factory, factory_code = generar_specification_factory(nombre_entidad, paquete, atributos_usados)

    # ✅ Crear carpetas si no existen
    os.makedirs("specifications", exist_ok=True)
    os.makedirs("factories", exist_ok=True)

    # ✅ Guardar archivos
    spec_file = os.path.join("specifications", f"{nombre_spec}.java")
    factory_file = os.path.join("factories", f"{nombre_factory}.java")

    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_code)
    with open(factory_file, "w", encoding="utf-8") as f:
        f.write(factory_code)

    print(f"✅ Specifications generado en: {spec_file}")
    print(f"✅ SpecificationFactory generado en: {factory_file}")

    return spec_code, factory_code  # Retorna los códigos generados

# Función auxiliar para extraer el paquete del código Java
def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
