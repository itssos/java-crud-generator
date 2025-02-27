import os
import re
import inquirer

def extraer_atributos(codigo_java):
    """
    Extrae los atributos de la clase Java.
    """
    return re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)

def buscar_embedded_en_dtos(dtos_path):
    """
    Busca si hay otros DTOs con @Embedded.
    """
    embedded_classes = set()
    for archivo in os.listdir(dtos_path):
        if archivo.endswith("Dto.java"):
            with open(os.path.join(dtos_path, archivo), "r", encoding="utf-8") as f:
                contenido = f.read()
                matches = re.findall(r'@Embedded\s+private\s+(\w+)', contenido)
                embedded_classes.update(matches)
    return embedded_classes

def buscar_embeddable_classes(src_path):
    """
    Busca clases anotadas con @Embeddable.
    """
    embeddable_classes = set()
    for root, _, files in os.walk(src_path):
        for archivo in files:
            if archivo.endswith(".java"):
                with open(os.path.join(root, archivo), "r", encoding="utf-8") as f:
                    contenido = f.read()
                    if "@Embeddable" in contenido:
                        match = re.search(r'public\s+class\s+(\w+)', contenido)
                        if match:
                            embeddable_classes.add(match.group(1))
    return embeddable_classes

def buscar_pojo(pojos_path, nombre_clase):
    """
    Busca una clase en el directorio de POJOs.
    """
    pojo_file = os.path.join(pojos_path, f"{nombre_clase}.java")
    if os.path.exists(pojo_file):
        return nombre_clase
    return None

def generar_dto(nombre_entidad, paquete, atributos_seleccionados, embedded_clases, pojo_clase):
    """
    Genera el código del DTO en base a los atributos seleccionados, clases embebidas y POJO.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_dto = f"{nombre_simple}Dto"
    paquete_dto = paquete.replace("models.entities", "models.dtos")
    
    importaciones = set([
        "import lombok.AllArgsConstructor;",
        "import lombok.Data;",
        "import lombok.EqualsAndHashCode;",
        "import lombok.RequiredArgsConstructor;",
        "import lombok.experimental.SuperBuilder;"
    ])
    
    if pojo_clase:
        importaciones.add(f"import {paquete.replace('models.entities', 'models.pojos')}.{pojo_clase};")
    
    atributos_str = []
    for tipo, nombre in atributos_seleccionados:
        if "id" in nombre.lower() or "Id" in nombre:
            atributos_str.append(f"@NotNull\n    private {tipo} {nombre};")
            importaciones.add("import jakarta.validation.constraints.NotNull;")
        else:
            atributos_str.append(f"private {tipo} {nombre};")
    
    embedded_str = []
    for clase in embedded_clases:
        embedded_str.append(f"@Embedded\n    private {clase} {clase.lower()};")
        importaciones.add("import jakarta.persistence.Embedded;")
    
    extends_str = f" extends {pojo_clase}" if pojo_clase else ""
    
    dto_code = f"""package {paquete_dto};

{chr(10).join(importaciones)}

@EqualsAndHashCode(callSuper = true)
@SuperBuilder
@AllArgsConstructor
@RequiredArgsConstructor
@Data
public class {nombre_dto}{extends_str} {{

    {chr(10).join(atributos_str)}
    {chr(10).join(embedded_str)}
}}
"""
    return dto_code

def generar_dto_archivo(entidad_file, dtos_path, src_path, pojos_path):
    """
    Genera el DTO en base a una entidad Java.
    """
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()
    
    nombre_entidad = re.search(r'public\s+class\s+(\w+)', codigo_java)
    nombre_entidad = nombre_entidad.group(1) if nombre_entidad else None
    
    paquete = re.search(r'package\s+([\w\.]+);', codigo_java)
    paquete = paquete.group(1) if paquete else "com.example.models.entities"
    
    atributos = extraer_atributos(codigo_java)
    if not nombre_entidad or not atributos:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos.")
        return
    
    nombre_pojo = nombre_entidad.replace("Entity", "")
    pojo_clase = buscar_pojo(pojos_path, nombre_pojo)
    
    # Buscar clases embebidas en DTOs existentes
    embedded_clases_dtos = buscar_embedded_en_dtos(dtos_path)
    embeddable_clases = buscar_embeddable_classes(src_path)
    
    # Preguntar al usuario qué atributos incluir
    preguntas = [
        inquirer.Checkbox(
            "atributos",
            message="Seleccione los atributos a incluir en el DTO:",
            choices=[f"{tipo} {nombre}" for tipo, nombre in atributos],
        )
    ]
    respuestas = inquirer.prompt(preguntas)
    atributos_seleccionados = [tuple(attr.split(" ")) for attr in respuestas["atributos"]] if respuestas else []
    
    # Preguntar si se quieren incluir clases embebidas
    if embedded_clases_dtos or embeddable_clases:
        preguntas_embedded = [
            inquirer.Checkbox(
                "embedded",
                message="Seleccione clases embebidas a incluir:",
                choices=list(embedded_clases_dtos | embeddable_clases),
            )
        ]
        respuestas_embedded = inquirer.prompt(preguntas_embedded)
        embedded_clases = respuestas_embedded["embedded"] if respuestas_embedded else []
    else:
        embedded_clases = []
    
    # Generar código DTO
    dto_code = generar_dto(nombre_entidad, paquete, atributos_seleccionados, embedded_clases, pojo_clase)
    
    # Guardar archivo
    os.makedirs(dtos_path, exist_ok=True)
    dto_file = os.path.join(dtos_path, f"{nombre_entidad.replace('Entity', '')}Dto.java")
    with open(dto_file, "w", encoding="utf-8") as f:
        f.write(dto_code)
    
    print(f"✅ DTO generado: {dto_file}")
