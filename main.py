import os

from gen.controller import (
    generar_get_controller,
    generar_post_controller,
    generar_delete_controller,
    generar_patch_controller,
    generar_search_controller
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
from gen.pojo import generar_pojo_archivo  # 🔹 Generador de POJOs
from gen.search import generar_search_model_archivo, extraer_atributos, seleccionar_atributos
from gen.specification import generar_specifications_archivo
from gen.mapper import generar_mapper_archivo
from gen.factories import generar_archivos_factories

def main():
    # Ruta del archivo de la entidad Java
    entidad_file = "C:\\Users\\diego\\OneDrive\\Documentos\\Github\\java-crud-generator\\PatientEntity.java"

    # Verificar si el archivo existe
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

    # Crear carpetas si no existen
    os.makedirs("repositories", exist_ok=True)
    os.makedirs("services", exist_ok=True)
    os.makedirs("controllers", exist_ok=True)
    os.makedirs("models/dtos", exist_ok=True)
    os.makedirs("models/pojos", exist_ok=True)  # Crear carpeta para POJOs
    os.makedirs("search", exist_ok=True)
    os.makedirs("mappers", exist_ok=True)

    # Generar archivos DTO y POJO
    generar_dto_archivo(entidad_file, "models/dtos", "models/dtos", "models/pojos")
    generar_pojo_archivo(entidad_file, "models/pojos")

    # Extraer atributos y solicitar selección (se hace una sola vez)
    atributos = extraer_atributos(codigo_java)
    if not atributos:
        print("❌ No se pudieron extraer los atributos de la entidad.")
        return
    atributos_seleccionados = seleccionar_atributos(atributos)
    if not atributos_seleccionados:
        print("⚠ No se seleccionaron atributos. Abortando generación de SearchModel y Specifications.")
        return

    # Generar SearchModel y Specifications utilizando los mismos atributos seleccionados
    generar_search_model_archivo(entidad_file, atributos_seleccionados)
    generar_specifications_archivo(entidad_file, atributos_seleccionados)
    generar_archivos_factories(entidad_file, atributos_seleccionados)

    # Generar Mapper
    generar_mapper_archivo(entidad_file)

    # Generar Repository
    repo_code = generar_repository(nombre_entidad, paquete)
    repo_file = os.path.join("repositories", f"{nombre_simple}Repository.java")
    with open(repo_file, "w", encoding="utf-8") as f:
        f.write(repo_code)

    # Generar Services
    services_map = {
        f"Create{nombre_simple}Service.java": generar_create_service(nombre_entidad, paquete),
        f"Find{nombre_simple}Service.java": generar_find_service(nombre_entidad, paquete),
        f"Patch{nombre_simple}Service.java": generar_patch_service(nombre_entidad, paquete),
        f"Delete{nombre_simple}Service.java": generar_delete_service(nombre_entidad, paquete),
        f"Search{nombre_simple}Service.java": generar_search_service(nombre_entidad, paquete),
    }
    for filename, code in services_map.items():
        with open(os.path.join("services", filename), "w", encoding="utf-8") as f:
            f.write(code)

    # Generar Controllers
    controllers_map = {
        f"Post{nombre_simple}Controller.java": generar_post_controller(nombre_entidad, paquete),
        f"Get{nombre_simple}Controller.java": generar_get_controller(nombre_entidad, paquete),
        f"Patch{nombre_simple}Controller.java": generar_patch_controller(nombre_entidad, paquete),
        f"Delete{nombre_simple}Controller.java": generar_delete_controller(nombre_entidad, paquete),
        f"Search{nombre_simple}Controller.java": generar_search_controller(nombre_entidad, paquete),
    }
    for filename, code in controllers_map.items():
        with open(os.path.join("controllers", filename), "w", encoding="utf-8") as f:
            f.write(code)

    # Mensaje final de confirmación
    print("✅ Generación de código completada.")
    print(f"📁 Revisa las carpetas 'repositories', 'services', 'controllers', 'models/dtos', 'models/pojos', 'search' y 'mappers'.")

if __name__ == "__main__":
    main()
