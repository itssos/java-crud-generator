import os
import shutil

from gen.controller import (
    generar_get_controller,
    generar_post_controller,
    generar_delete_controller,
    generar_patch_controller,
)

from gen.service import (
    generar_create_service,
    generar_delete_service,
    generar_find_service,
    generar_patch_service,
    generar_search_service
)
from gen.repository import generar_repository
from extract_data import extraer_nombre_entidad, extraer_paquete
from gen.dto import generar_dto_archivo
from gen.pojo import generar_pojo_archivo  # Generador de POJOs
from gen.mapper import generar_mapper_archivo
from gen.search import generar_search_model_archivo, extraer_atributos, seleccionar_atributos
from gen.specification import generar_specifications_archivo
from gen.factories import generar_archivos_factories


def seleccionar_archivo(entidad_dir):
    """
    Lista los archivos .java en el directorio y permite al usuario seleccionar uno.
    """
    archivos = [f for f in os.listdir(entidad_dir) if f.endswith(".java")]
    if not archivos:
        print("❌ No se encontraron archivos Java en el directorio.")
        return None
    if len(archivos) == 1:
        return os.path.join(entidad_dir, archivos[0])
    # Si hay varios, mostrar opciones
    print("Archivos encontrados:")
    for idx, archivo in enumerate(archivos, start=1):
        print(f"{idx}. {archivo}")
    while True:
        eleccion = input("Seleccione el número del archivo que desea procesar: ").strip()
        if eleccion.isdigit():
            indice = int(eleccion) - 1
            if 0 <= indice < len(archivos):
                return os.path.join(entidad_dir, archivos[indice])
        print("❌ Selección inválida. Intente de nuevo.")


def main():
    # Solicitar por consola el directorio que contiene las entidades
    entidad_dir = input("Ingrese el directorio que contiene las entidades: ").strip()
    if not os.path.isdir(entidad_dir):
        print(f"❌ El directorio '{entidad_dir}' no existe.")
        return

    # Permitir al usuario seleccionar el archivo de entidad a procesar
    entidad_file = seleccionar_archivo(entidad_dir)
    if not entidad_file:
        return

    # Verificar si el archivo existe (por precaución)
    if not os.path.exists(entidad_file):
        print(f"❌ Error: El archivo no existe en la ruta: {entidad_file}")
        return

    # Leer el código de la entidad
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer metadatos
    nombre_entidad = extraer_nombre_entidad(codigo_java)
    paquete = extraer_paquete(codigo_java)
    nombre_simple = nombre_entidad.replace("Entity", "")

    if not nombre_entidad or not paquete:
        print("❌ No se pudo extraer el nombre de la entidad o el paquete.")
        return

    # Mover (copiar) la entidad seleccionada a output/models/entities/
    entities_out_dir = os.path.join("output", "models", "entities")
    os.makedirs(entities_out_dir, exist_ok=True)
    shutil.copy(entidad_file, os.path.join(entities_out_dir, os.path.basename(entidad_file)))
    print(f"✅ Entidad copiada a: {os.path.join(entities_out_dir, os.path.basename(entidad_file))}")

    # Solicitar el valor para la constante compartida (para POST, PATCH y DELETE)
    con_value_input = input("Ingrese el valor para la constante compartida para el controlador (por ejemplo, 40): ").strip()
    if not con_value_input.isdigit():
        print("❌ Debe ingresar un número válido.")
        return
    con_value = con_value_input

    # Crear carpetas dentro de la carpeta 'output' si no existen
    output_dirs = {
        "controllers": os.path.join("output", "controllers"),
        "services": os.path.join("output", "services"),
        "repositories": os.path.join("output", "repositories"),
        "models_dtos": os.path.join("output", "models", "dtos"),
        "models_pojos": os.path.join("output", "models", "pojos"),
        "mappers": os.path.join("output", "mappers"),
        "search": os.path.join("output", "search"),
        "specifications": os.path.join("output", "specifications"),
        "factories": os.path.join("output", "factories")
    }

    for dir_path in output_dirs.values():
        os.makedirs(dir_path, exist_ok=True)

    # 1. Generar Controllers (GET no utiliza la constante)
    controllers_map = {
        f"Post{nombre_simple}Controller.java": generar_post_controller(nombre_entidad, paquete, con_value),
        f"Get{nombre_simple}Controller.java": generar_get_controller(nombre_entidad, paquete),
        f"Patch{nombre_simple}Controller.java": generar_patch_controller(nombre_entidad, paquete, con_value),
        f"Delete{nombre_simple}Controller.java": generar_delete_controller(nombre_entidad, paquete, con_value),
    }
    for filename, code in controllers_map.items():
        filepath = os.path.join(output_dirs["controllers"], filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

    # 2. Generar Services
    services_map = {
        f"Create{nombre_simple}Service.java": generar_create_service(nombre_entidad, paquete),
        f"Find{nombre_simple}Service.java": generar_find_service(nombre_entidad, paquete),
        f"Patch{nombre_simple}Service.java": generar_patch_service(nombre_entidad, paquete),
        f"Delete{nombre_simple}Service.java": generar_delete_service(nombre_entidad, paquete),
        f"Search{nombre_simple}Service.java": generar_search_service(nombre_entidad, paquete),
    }
    for filename, code in services_map.items():
        filepath = os.path.join(output_dirs["services"], filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

    # 3. Generar Repository
    repo_code = generar_repository(nombre_entidad, paquete)
    repo_file = os.path.join(output_dirs["repositories"], f"{nombre_simple}Repository.java")
    with open(repo_file, "w", encoding="utf-8") as f:
        f.write(repo_code)

    # 4. Generar archivos DTO y POJO
    generar_pojo_archivo(entidad_file, output_dirs["models_pojos"])
    generar_dto_archivo(entidad_file, output_dirs["models_dtos"], output_dirs["models_dtos"], output_dirs["models_pojos"])

    # 5. Generar Mapper
    generar_mapper_archivo(entidad_file)

    # 6. Extraer atributos y solicitar selección (se hace una sola vez)
    atributos = extraer_atributos(codigo_java)
    if not atributos:
        print("❌ No se pudieron extraer los atributos de la entidad.")
        return
    atributos_seleccionados = seleccionar_atributos(atributos)
    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. Abortando generación de SearchModel, Specifications y Factories.")
        return

    # 7. Generar SearchModel, Specifications y Factories utilizando los mismos atributos seleccionados
    generar_search_model_archivo(entidad_file, atributos_seleccionados)
    generar_specifications_archivo(entidad_file, atributos_seleccionados)
    generar_archivos_factories(entidad_file, atributos_seleccionados)

    print("✅ Generación de código completada.")
    print("📁 Revisa la carpeta 'output' y sus subcarpetas: controllers, services, repositories, models/dtos, models/entities, models/pojos, mappers, search, specifications y factories.")


if __name__ == "__main__":
    main()
