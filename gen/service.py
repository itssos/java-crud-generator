def generar_create_service(nombre_entidad, paquete, id_tipo="Long"):
    nombre_simple = nombre_entidad.replace("Entity", "")
    var_name = nombre_simple[0].lower() + nombre_simple[1:]
    return f"""package {paquete}.services;

import {paquete}.mappers.{nombre_simple}Mapper;
import {paquete}.models.dtos.{nombre_simple}Dto;
import {paquete}.models.pojos.{nombre_simple};
import {paquete}.repositories.{nombre_simple}Repository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class Create{nombre_simple}Service {{
    private final {nombre_simple}Repository repository;

    public {nombre_simple}Dto create(final {nombre_simple} {var_name}) {{
        {var_name}.setHighQuality(Boolean.FALSE);
        return {nombre_simple}Mapper.toDto(repository.save({nombre_simple}Mapper.toEntity({var_name})));
    }}
}}
"""


def generar_find_service(nombre_entidad, paquete, id_tipo="Long"):
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {paquete}.services;

import org.springframework.stereotype.Service;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.repositories.{nombre_simple}Repository;
import java.util.Optional;

@Service
public class Find{nombre_simple}Service {{

    private final {nombre_simple}Repository repository;

    public Find{nombre_simple}Service({nombre_simple}Repository repository) {{
        this.repository = repository;
    }}

    public {nombre_entidad} findById({id_tipo} id) {{
        Optional<{nombre_entidad}> result = repository.findById(id);
        return result.orElse(null);
    }}
}}
"""

def generar_patch_service(nombre_entidad, paquete, id_tipo="Long"):
    """
    Ejemplo simple de patch, asumiendo que solo modificamos
    algunos campos. Ajusta la lógica según tus requisitos.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {paquete}.services;

import org.springframework.stereotype.Service;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.repositories.{nombre_simple}Repository;
import java.util.Optional;

@Service
public class Patch{nombre_simple}Service {{

    private final {nombre_simple}Repository repository;

    public Patch{nombre_simple}Service({nombre_simple}Repository repository) {{
        this.repository = repository;
    }}

    public {nombre_entidad} patch({id_tipo} id, {nombre_entidad} partialEntity) {{
        Optional<{nombre_entidad}> existingOpt = repository.findById(id);
        if (existingOpt.isEmpty()) {{
            return null; // O lanza excepción
        }}

        {nombre_entidad} existing = existingOpt.get();
        // Ejemplo: parchear sólo algunos campos no nulos
        if (partialEntity.getName() != null) {{
            existing.setName(partialEntity.getName());
        }}
        if (partialEntity.getSurname() != null) {{
            existing.setSurname(partialEntity.getSurname());
        }}
        // Agrega aquí más lógica para otros campos

        return repository.save(existing);
    }}
}}
"""

def generar_delete_service(nombre_entidad, paquete, id_tipo="Long"):
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {paquete}.services;

import org.springframework.stereotype.Service;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.repositories.{nombre_simple}Repository;

@Service
public class Delete{nombre_simple}Service {{

    private final {nombre_simple}Repository repository;

    public Delete{nombre_simple}Service({nombre_simple}Repository repository) {{
        this.repository = repository;
    }}

    public void delete({id_tipo} id) {{
        repository.deleteById(id);
    }}
}}
"""

def generar_search_service(nombre_entidad, paquete):
    """
    Servicio para búsqueda/listado (GET /patients).
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {paquete}.services;

import org.springframework.stereotype.Service;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.repositories.{nombre_simple}Repository;
import java.util.List;

@Service
public class Search{nombre_simple}Service {{

    private final {nombre_simple}Repository repository;

    public Search{nombre_simple}Service({nombre_simple}Repository repository) {{
        this.repository = repository;
    }}

    public List<{nombre_entidad}> searchAll() {{
        return repository.findAll();
    }}
}}
"""