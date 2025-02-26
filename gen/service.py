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
    nombre_var = nombre_simple[0].lower() + nombre_simple[1:]
    return f"""package {paquete}.services;

import {paquete}.exceptions.CwsException;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.repositories.{nombre_simple}Repository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class Find{nombre_simple}Service {{
    private final {nombre_simple}Repository repository;

    public {nombre_entidad} find(final {id_tipo} {nombre_var}Id) {{
        return repository.findById({nombre_var}Id)
                         .orElseThrow(() -> new CwsException("Not found " + {nombre_var}Id));
    }}
}}
"""

def generar_patch_service(nombre_entidad, paquete, id_tipo="Long"):
    """
    Genera el servicio de PATCH que utiliza el FindService para obtener la entidad existente,
    el Mapper para transformar el POJO en entidad, y PatchUtils para mezclar ambos.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_var = nombre_simple[0].lower() + nombre_simple[1:]
    return f"""package {paquete}.services;

import {paquete}.mappers.{nombre_simple}Mapper;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.models.pojos.{nombre_simple};
import {paquete}.repositories.{nombre_simple}Repository;
import {paquete}.services.Find{nombre_simple}Service;
import {paquete}.utils.PatchUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class Patch{nombre_simple}Service {{
    private final Find{nombre_simple}Service service;
    private final {nombre_simple}Repository repository;

    public void patch(final {id_tipo} {nombre_var}Id, final {nombre_simple} {nombre_var}Patch) {{
        final {nombre_entidad} existingEntity = service.find({nombre_var}Id);
        final {nombre_entidad} patchedEntity = {nombre_simple}Mapper.toEntity({nombre_var}Patch);
        repository.save(PatchUtils.merge(existingEntity, patchedEntity));
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