def generar_repository(nombre_entidad, paquete, id_tipo="Long"):
    """
    Genera el código de la interfaz Repository, p. ej. PatientRepository.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {paquete}.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import {paquete}.models.entities.{nombre_entidad};

public interface {nombre_simple}Repository extends JpaRepository<{nombre_entidad}, {id_tipo}> {{
}}
"""