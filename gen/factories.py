import os
import re

def extraer_atributos_search(codigo_java):
    """
    Extrae los atributos de la clase SearchModel Java.
    Busca variables privadas con su tipo de dato y nombre.
    """
    return re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)

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

    # Construcción de la lista de especificaciones
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
    return factory_code

def generar_specification_factory_archivo(entidad_file):
    """
    Lee el archivo de la entidad y genera la SpecificationFactory correspondiente desde SearchModel.
    """

    # Obtener el nombre base de la entidad
    nombre_entidad = os.path.basename(entidad_file).replace(".java", "").replace("Entity", "")
    search_file = os.path.join("search", f"{nombre_entidad}SearchModel.java")

    # Verificar si el SearchModel existe antes de generar el SpecificationFactory
    if not os.path.exists(search_file):
        print(f"❌ Error: No se encontró el archivo SearchModel en: {search_file}")
        print("⚠ Asegúrate de ejecutar primero la generación del SearchModel.")
        return

    # Leer código Java del SearchModel
    with open(search_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer metadatos
    paquete = extraer_paquete(codigo_java)
    atributos = extraer_atributos_search(codigo_java)

    # Validar si se encontraron atributos
    if not atributos:
        print("⚠ Advertencia: No se encontraron atributos en el SearchModel. No se generará el SpecificationFactory.")
        return

    # Generar SpecificationFactory
    factory_code = generar_specification_factory(nombre_entidad, paquete, atributos)

    # Crear carpeta si no existe
    os.makedirs("factories", exist_ok=True)

    # Guardar archivo
    factory_file = os.path.join("factories", f"{nombre_entidad}SpecificationFactory.java")
    with open(factory_file, "w", encoding="utf-8") as f:
        f.write(factory_code)

    print(f"✅ SpecificationFactory generado correctamente: {factory_file}")

# Funciones auxiliares para extraer nombre de entidad y paquete
def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
