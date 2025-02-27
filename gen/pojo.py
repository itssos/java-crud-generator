import os
import re
import inquirer

def extraer_constantes_estaticas(codigo_java):
    """
    Extrae las constantes estáticas de la clase Java y las devuelve en un diccionario.
    """
    constantes = {}
    matches = re.findall(r'private\s+static\s+final\s+int\s+(\w+)\s*=\s*(\d+);', codigo_java)
    for nombre, valor in matches:
        constantes[nombre] = int(valor)
    return constantes

def extraer_atributos_para_pojo(codigo_java, constantes):
    """
    Extrae todos los atributos de la clase Java, incluyendo los que tienen validación de longitud.
    """
    atributos = []

    # Extraer atributos con @Column(length = ...)
    matches = re.findall(r'@Column\(.*?length\s*=\s*(\w+)\)\s*private\s+([\w<>]+)\s+(\w+);', codigo_java)
    for constante, tipo, nombre in matches:
        if constante in constantes:  
            atributos.append((tipo, nombre, constante))

    # Extraer atributos sin @Column
    matches_sin_column = re.findall(r'private\s+([\w<>]+)\s+(\w+);', codigo_java)
    for tipo, nombre in matches_sin_column:
        # Evitar agregar atributos duplicados
        if not any(attr[1] == nombre for attr in atributos):
            atributos.append((tipo, nombre, None))  # None indica que no tiene longitud definida

    return atributos

def generar_pojo(nombre_entidad, paquete, atributos_seleccionados, constantes_usadas):
    """
    Genera el código del POJO basado en los atributos seleccionados y las constantes utilizadas.
    """
    nombre_pojo = nombre_entidad.replace("Entity", "")
    paquete_pojo = paquete.replace("models.entities", "models.pojos")

    importaciones = {
        "import lombok.AllArgsConstructor;",
        "import lombok.Data;",
        "import lombok.NoArgsConstructor;",
        "import lombok.experimental.SuperBuilder;"
    }

    # Verificar si hay atributos de tipo LocalDate para agregar la importación
    if any(tipo == "LocalDate" for tipo, _, _ in atributos_seleccionados):
        importaciones.add("import java.time.LocalDate;")

    # Generar solo las constantes utilizadas
    constantes_str = [f"    private static final int {nombre} = {valor};" for nombre, valor in constantes_usadas.items()]

    atributos_str = []
    for tipo, nombre, max_length in atributos_seleccionados:
        if max_length:  # Solo agregar @Size si tiene un max_length definido
            atributos_str.append(f"    @Size(max = {max_length})\n    private {tipo} {nombre};")
            importaciones.add("import jakarta.validation.constraints.Size;")
        else:
            atributos_str.append(f"    private {tipo} {nombre};")

    pojo_code = f"""package {paquete_pojo};

{chr(10).join(importaciones)}

@SuperBuilder
@Data
@AllArgsConstructor
@NoArgsConstructor
public class {nombre_pojo} {{

{chr(10).join(constantes_str)}

{chr(10).join(atributos_str)}
}}"""
    return pojo_code

def generar_pojo_archivo(entidad_file, pojos_path):
    """
    Genera el POJO en base a una entidad Java, extrayendo sus constantes y atributos.
    """
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()
    
    nombre_entidad = re.search(r'public\s+class\s+(\w+)', codigo_java)
    if not nombre_entidad:
        print("❌ Error: No se pudo extraer el nombre de la entidad.")
        return
    
    nombre_entidad = nombre_entidad.group(1)
    
    paquete = re.search(r'package\s+([\w\.]+);', codigo_java)
    paquete = paquete.group(1) if paquete else "com.example.models.entities"
    
    constantes = extraer_constantes_estaticas(codigo_java)
    atributos = extraer_atributos_para_pojo(codigo_java, constantes)
    
    if not atributos:
        print("❌ Error: No se encontraron atributos en la entidad.")
        return

    # Mostrar todos los atributos en la consola
    print("\n🔹 Atributos detectados en la entidad:")
    for tipo, nombre, max_length in atributos:
        print(f"   - {tipo} {nombre} (max_length: {max_length if max_length else 'N/A'})")

    # Preguntar al usuario qué atributos incluir
    preguntas = [
        inquirer.Checkbox(
            "atributos",
            message="Seleccione los atributos a incluir en el POJO:",
            choices=[f"{tipo} {nombre}" for tipo, nombre, _ in atributos],
        )
    ]
    respuestas = inquirer.prompt(preguntas)
    atributos_seleccionados = [attr for attr in atributos if f"{attr[0]} {attr[1]}" in respuestas["atributos"]] if respuestas else []

    # Filtrar constantes que realmente se usan
    constantes_usadas = {nombre: valor for nombre, valor in constantes.items() if nombre in [attr[2] for attr in atributos_seleccionados]}

    # Generar código POJO
    pojo_code = generar_pojo(nombre_entidad, paquete, atributos_seleccionados, constantes_usadas)

    # Guardar archivo
    os.makedirs(pojos_path, exist_ok=True)
    pojo_file = os.path.join(pojos_path, f"{nombre_entidad.replace('Entity', '')}.java")
    with open(pojo_file, "w", encoding="utf-8") as f:
        f.write(pojo_code)

    print(f"\n✅ POJO generado: {pojo_file}")
