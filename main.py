import re
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
from gen.dto import generar_dto_archivo  # ✅ Importamos el generador de DTO
from gen.search import generar_search_model_archivo  # ✅ Importamos el generador de SearchModel

def main():
    # Nombre de tu archivo .java
        entidad_file = "D:\Digital Solutions\AutoCrud\pruebas\patients-api\src\main\java\com\inycom\cws\models\entities\PatientEntity.java"

    # Leer el código Java
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    # Extraer metadatos
    nombre_entidad = extraer_nombre_entidad(codigo_java)
    paquete = extraer_paquete(codigo_java)

    if not nombre_entidad:
        print("❌ No se pudo extraer el nombre de la entidad.")
        return

    # Crear subcarpetas si no existen
    os.makedirs("repositories", exist_ok=True)
    os.makedirs("services", exist_ok=True)
    os.makedirs("controllers", exist_ok=True)
    os.makedirs("models/dtos", exist_ok=True)  # ✅ Aseguramos la carpeta de DTOs
    os.makedirs("search", exist_ok=True)  # ✅ Ahora `search/` está fuera de `models/`

    # ✅ Generar DTO en `models/dtos/`
    generar_dto_archivo(entidad_file)

    # ✅ Generar SearchModel en `search/`
    generar_search_model_archivo(entidad_file)

    # Generar Repository
    repo_code = generar_repository(nombre_entidad, paquete)
    repo_file = os.path.join("repositories", nombre_entidad.replace("Entity", "") + "Repository.java")
    with open(repo_file, "w", encoding="utf-8") as f:
        f.write(repo_code)

    # Generar Services
    services_map = {
        f"Create{nombre_entidad.replace('Entity','')}Service.java": generar_create_service(nombre_entidad, paquete),
        f"Find{nombre_entidad.replace('Entity','')}Service.java": generar_find_service(nombre_entidad, paquete),
        f"Patch{nombre_entidad.replace('Entity','')}Service.java": generar_patch_service(nombre_entidad, paquete),
        f"Delete{nombre_entidad.replace('Entity','')}Service.java": generar_delete_service(nombre_entidad, paquete),
        f"Search{nombre_entidad.replace('Entity','')}Service.java": generar_search_service(nombre_entidad, paquete),
    }

    for filename, code in services_map.items():
        with open(os.path.join("services", filename), "w", encoding="utf-8") as f:
            f.write(code)

    # Generar Controllers
    controllers_map = {
        f"Post{nombre_entidad.replace('Entity','')}Controller.java": generar_post_controller(nombre_entidad, paquete),
        f"Get{nombre_entidad.replace('Entity','')}Controller.java": generar_get_controller(nombre_entidad, paquete),
        f"Patch{nombre_entidad.replace('Entity','')}Controller.java": generar_patch_controller(nombre_entidad, paquete),
        f"Delete{nombre_entidad.replace('Entity','')}Controller.java": generar_delete_controller(nombre_entidad, paquete),
        f"Search{nombre_entidad.replace('Entity','')}Controller.java": generar_search_controller(nombre_entidad, paquete),
    }

    for filename, code in controllers_map.items():
        with open(os.path.join("controllers", filename), "w", encoding="utf-8") as f:
            f.write(code)

    print("✅ Generación de código completada.")
    print("📂 Revisa las carpetas 'repositories', 'services', 'controllers', 'models/dtos' y 'search'.")

if __name__ == "__main__":
    main()
