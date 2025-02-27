import os
import re

def extraer_atributos(codigo_java):
    """
    Extrae los atributos de la entidad eliminando anotaciones de JPA.
    """
    atributos = []
    for linea in codigo_java.splitlines():
        linea = linea.strip()
        if linea.startswith("private "):
            tipo_nombre = linea.replace("private ", "").replace(";", "").split(" ")
            if len(tipo_nombre) == 2:
                tipo, nombre = tipo_nombre
                atributos.append((tipo, nombre))
    return atributos

def extraer_paquete(codigo_java):
    match = re.search(r'package\s+([\w\.]+);', codigo_java)
    return match.group(1) if match else "com.example"

def extraer_nombre_entidad(codigo_java):
    match = re.search(r'public\s+class\s+(\w+)', codigo_java)
    return match.group(1) if match else None

def generar_pojo(nombre_entidad, paquete, atributos):
    """
    Genera el código del POJO basado en la entidad.
    """
    nombre_pojo = nombre_entidad.replace("Entity", "")
    
    importaciones = """import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;
import java.io.Serializable;
import java.util.List;
import java.util.Collection;
"""
    
    atributos_str = "\n    ".join([f"private {tipo} {nombre};" for tipo, nombre in atributos])
    
    pojo_code = f"""package {paquete}.pojos;

{importaciones}

@SuperBuilder
@Data
@AllArgsConstructor
@NoArgsConstructor
public class {nombre_pojo} implements Serializable {{

    {atributos_str}
}}
"""
    return pojo_code

def generar_pojo_archivo(entidad_file):
    """
    Lee el archivo de la entidad y genera el POJO correspondiente.
    """
    with open(entidad_file, "r", encoding="utf-8") as f:
        codigo_java = f.read()

    nombre_entidad = extraer_nombre_entidad(codigo_java)
    paquete = extraer_paquete(codigo_java)
    atributos = extraer_atributos(codigo_java)

    if not nombre_entidad or not atributos:
        print("❌ Error: No se pudo extraer el nombre de la entidad o los atributos.")
        return

    pojo_code = generar_pojo(nombre_entidad, paquete, atributos)

    os.makedirs("pojos", exist_ok=True)
    pojo_file = os.path.join("pojos", f"{nombre_entidad.replace('Entity', '')}.java")
    with open(pojo_file, "w", encoding="utf-8") as f:
        f.write(pojo_code)

    print(f"✅ POJO generado en: {pojo_file}")

# Si se ejecuta directamente, probar la generación
if __name__ == "__main__":
    entidad_file = "./entities/ExampleEntity.java"  # Cambiar a una entidad real
    generar_pojo_archivo(entidad_file)
