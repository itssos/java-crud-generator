import os
import re
import inquirer

def extraer_atributos(codigo_java):
    """
    Extrae todos los atributos de la clase Java.
    Retorna una lista de tuplas (tipo, nombre).
    """
    return re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)

def extraer_embedded_atributos(codigo_java):
    """
    Extrae de la entidad los atributos que están anotados con @Embedded.
    Retorna una lista de tuplas (tipo, nombre).
    """
    return re.findall(r'@Embedded\s+private\s+([\w<>]+)\s+(\w+);', codigo_java)

def extraer_id_atributo(codigo_java):
    """
    Extrae el atributo que está anotado con @Id, incluso si tiene anotaciones intermedias.
    Retorna una tupla (tipo, nombre) si se encuentra, o None en caso contrario.
    Se permite que entre @Id y "private" haya anotaciones que contengan cualquier carácter.
    """
    pattern = r'@Id(?:\s*\n\s*@.*?)*\s*private\s+([\w<>]+)\s+(\w+);'
    match = re.search(pattern, codigo_java, re.DOTALL)
    if match:
        return (match.group(1), match.group(2))
    return None

def buscar_embeddable_classes(entidades_path):
    """
    Busca clases anotadas con @Embeddable en la carpeta models/entities.
    """
    embeddable_classes = set()
    for archivo in os.listdir(entidades_path):
        if archivo.endswith(".java"):
            with open(os.path.join(entidades_path, archivo), "r", encoding="utf-8") as f:
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

def generar_dto(nombre_entidad, paquete, atributos_seleccionados, embedded_seleccionados, pojo_clase, id_atributo):
    """
    Genera el código del DTO en base a:
      - Los atributos seleccionados.
      - Los atributos embebidos (con @Embedded) seleccionados.
      - Extiende del POJO, importándolo desde el package derivado de la entidad.
    Solo se añade @NotNull al atributo que corresponde al id (según la anotación @Id en la entidad).
    Cada línea (anotación y atributo) se indenta con un tabulador.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_dto = f"{nombre_simple}Dto"
    # Derivar package del DTO cambiando "models.entities" por "models.dtos"
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
        if id_atributo and nombre == id_atributo[1]:
            # Se añade @NotNull con tabulador antes
            atributos_str.append(f"\t@NotNull\n\tprivate {tipo} {nombre};")
            importaciones.add("import jakarta.validation.constraints.NotNull;")
        else:
            atributos_str.append(f"\tprivate {tipo} {nombre};")
    
    embedded_str = []
    for tipo, nombre in embedded_seleccionados:
        embedded_str.append(f"\t@Embedded\n\tprivate {tipo} {nombre};")
        importaciones.add("import jakarta.persistence.Embedded;")
    
    extends_str = f" extends {pojo_clase}" if pojo_clase else ""
    
    dto_code = f"""package {paquete_dto};

{chr(10).join(sorted(importaciones))}

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

def generar_dto_archivo(entidad_file, dtos_path, entidades_path, pojos_path):
    """
    Genera el DTO a partir de una entidad Java.
    Se extraen todos los atributos y se combinan en un solo prompt:
      - Los atributos que estén anotados con @Embedded se muestran con la etiqueta "(embedded)".
      - La selección se procesa para separar atributos normales y embebidos.
    El DTO extiende del POJO (si se encuentra) e importa dicho POJO desde el package derivado de la entidad.
    Solo se añade @NotNull al atributo que en la entidad está anotado con @Id.
    """
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()
    
    nombre_entidad_match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    nombre_entidad = nombre_entidad_match.group(1) if nombre_entidad_match else None
    
    paquete_match = re.search(r'package\s+([\w\.]+);', codigo_java)
    paquete = paquete_match.group(1) if paquete_match else "com.example.models.entities"
    
    atributos = extraer_atributos(codigo_java)
    if not nombre_entidad or not atributos:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos.")
        return
    
    id_atributo = extraer_id_atributo(codigo_java)
    
    nombre_pojo = nombre_entidad.replace("Entity", "")
    pojo_clase = buscar_pojo(pojos_path, nombre_pojo)
    
    embedded_atributos = extraer_embedded_atributos(codigo_java)
    embedded_nombres = {nombre for _, nombre in embedded_atributos}
    
    choices = []
    for tipo, nombre in atributos:
        if nombre in embedded_nombres:
            choices.append(f"{tipo} {nombre} (embedded)")
        else:
            choices.append(f"{tipo} {nombre}")
    
    preguntas = [
        inquirer.Checkbox(
            "atributos",
            message="Seleccione los atributos a incluir en el DTO:",
            choices=choices,
        )
    ]
    respuestas = inquirer.prompt(preguntas)
    
    atributos_seleccionados = []
    embedded_seleccionados = []
    if respuestas and "atributos" in respuestas:
        for attr in respuestas["atributos"]:
            if attr.endswith(" (embedded)"):
                attr_clean = attr.replace(" (embedded)", "")
                tipo, nombre = attr_clean.split(" ")
                embedded_seleccionados.append((tipo, nombre))
            else:
                tipo, nombre = attr.split(" ")
                atributos_seleccionados.append((tipo, nombre))
    
    dto_code = generar_dto(nombre_entidad, paquete, atributos_seleccionados, embedded_seleccionados, pojo_clase, id_atributo)
    
    os.makedirs(dtos_path, exist_ok=True)
    dto_file = os.path.join(dtos_path, f"{nombre_entidad.replace('Entity', '')}Dto.java")
    with open(dto_file, "w", encoding="utf-8") as f:
        f.write(dto_code)
    
    print(f"✅ DTO generado: {dto_file}")
