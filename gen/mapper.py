import os
import re

def extraer_base_paquete(paquete):
    """
    Extrae la base del package, por ejemplo, a partir de 
    "com.inycom.cws.models.entities" retorna "com.inycom.cws".
    """
    parts = paquete.split('.')
    if len(parts) >= 3:
        return '.'.join(parts[:3])
    return paquete

def generar_mapper(nombre_entidad, paquete):
    """
    Genera el código Java para un Mapper basado en la entidad, el DTO y el POJO.
    Se fija el package de los mappers en "com.inycom.cws.mappers".
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_dto = f"{nombre_simple}Dto"
    nombre_pojo = nombre_simple  # El POJO suele tener el mismo nombre sin "Entity"
    nombre_mapper = f"{nombre_simple}Mapper"
    
    # Extraer la base del package (por ejemplo, "com.inycom.cws")
    base = extraer_base_paquete(paquete)
    paquete_mapper = f"{base}.mappers"
    
    # Importaciones necesarias, usando la base para formar las rutas
    importaciones = f"""package {paquete_mapper};

import com.fasterxml.jackson.databind.ObjectMapper;
import {base}.factories.ObjectMapperFactory;
import {base}.models.dtos.{nombre_dto};
import {base}.models.entities.{nombre_entidad};
import {base}.models.pojos.{nombre_pojo};
import lombok.experimental.UtilityClass;
"""
    
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
    Lee el archivo de la entidad y genera el Mapper correspondiente, 
    guardándolo en output/mappers.
    """
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    nombre_entidad = extraer_nombre_entidad(codigo_java)
    paquete = extraer_paquete(codigo_java)

    if not nombre_entidad:
        print("❌ Error: No se pudo extraer el nombre de la entidad.")
        return

    mapper_code = generar_mapper(nombre_entidad, paquete)

    # Crear carpeta "output/mappers" si no existe
    mapper_dir = os.path.join("output", "mappers")
    os.makedirs(mapper_dir, exist_ok=True)
    mapper_file = os.path.join(mapper_dir, f"{nombre_entidad.replace('Entity', '')}Mapper.java")
    with open(mapper_file, "w", encoding="utf-8") as f:
        f.write(mapper_code)

    print(f"✅ Mapper generado en: {mapper_file}")

def extraer_nombre_entidad(codigo_java):
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"
