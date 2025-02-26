def generar_repository(nombre_entidad, paquete, id_tipo="Long"):
    """
    Genera el código de la interfaz Repository, p. ej. PatientRepository,
    extendiendo CrudRepository y JpaSpecificationExecutor, e incluyendo la anotación @Repository.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {paquete}.repositories;

import {paquete}.models.entities.{nombre_entidad};
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {nombre_simple}Repository extends CrudRepository<{nombre_entidad}, {id_tipo}>, JpaSpecificationExecutor<{nombre_entidad}> {{
}}
"""
