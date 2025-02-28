def extraer_base_paquete(paquete):
    """
    Extrae la base del package, por ejemplo:
    de "com.inycom.cws.models.entities" retorna "com.inycom.cws"
    """
    parts = paquete.split('.')
    if len(parts) >= 3:
        return '.'.join(parts[:3])
    return paquete

def generar_repository(nombre_entidad, paquete, id_tipo="Long"):
    base = extraer_base_paquete(paquete)
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {base}.repositories;

import {base}.models.entities.{nombre_entidad};
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {nombre_simple}Repository extends CrudRepository<{nombre_entidad}, {id_tipo}>, JpaSpecificationExecutor<{nombre_entidad}> {{
}}
"""
