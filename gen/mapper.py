import os
import re

def generar_mapper(nombre_entidad, paquete):
    """
    Genera el código Java para un Mapper basado en la entidad, el DTO y el POJO.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_dto = f"{nombre_simple}Dto"
    nombre_pojo = nombre_simple  # El POJO suele tener el mismo nombre sin `Entity`
    nombre_mapper = f"{nombre_simple}Mapper"

    # Importaciones necesarias
    importaciones = f"""package {paquete}.mappers;

import com.fasterxml.jackson.databind.ObjectMapper;
import {paquete}.factories.ObjectMapperFactory;
import {paquete}.models.dtos.{nombre_dto};
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.models.pojos.{nombre_pojo};
import lombok.experimental.UtilityClass;
"""

    # Código del Mapper
    mapper_code = f"""{importaciones}

@UtilityClass
public class {nombre_mapper} {{
    private static final ObjectMapper OBJECT_MAPPER = ObjectMapperFactory.create();

    public static {nombre_dto} toDto(final {nombre_entidad} entity) {{
        return OBJECT_MAPPER.convertValue(entity, {nombre_dto}.class);
    }}

    public static {nombre_entidad} toEntity(final {nombre_pojo} pojo) {{
        return OBJECT_MAPPER.convertValue(pojo, {nombre_entidad}.class);
    }}
}}
"""
    return mapper_code

def generar_mapper_archivo(entidad_file):
    """
    Lee el archivo de la entidad y genera el Mapper correspondiente.
    """
    # Leer código Java de la entidad
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer metadatos
    nombre_entidad = extraer_nombre_entidad(codigo_java)
    paquete = extraer_paquete(codigo_java)

    if not nombre_entidad:
        print("❌ Error: No se pudo extraer el nombre de la entidad.")
        return

    # Generar código del Mapper
    mapper_code = generar_mapper(nombre_entidad, paquete)

    # Crear carpeta `mappers` si no existe
    os.makedirs("mappers", exist_ok=True)

    # Guardar archivo en `mappers/`
    mapper_file = os.path.join("mappers", f"{nombre_entidad.replace('Entity', '')}Mapper.java")
    with open(mapper_file, "w", encoding="utf-8") as f:
        f.write(mapper_code)

    print(f"✅ Mapper generado en: {mapper_file}")

# Funciones auxiliares para extraer metadatos de la entidad
def extraer_nombre_entidad(codigo_java):
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
