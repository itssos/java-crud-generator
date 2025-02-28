def extraer_base_paquete(paquete):
    """
    Extrae la base del package, por ejemplo:
    de "com.inycom.cws.models.entities" retorna "com.inycom.cws"
    """
    parts = paquete.split('.')
    if len(parts) >= 3:
        return '.'.join(parts[:3])
    return paquete


def generar_create_service(nombre_entidad, paquete, id_tipo="Long"):
    base = extraer_base_paquete(paquete)
    nombre_simple = nombre_entidad.replace("Entity", "")
    var_name = nombre_simple[0].lower() + nombre_simple[1:]
    return f"""package {base}.services;

import {base}.mappers.{nombre_simple}Mapper;
import {base}.models.dtos.{nombre_simple}Dto;
import {base}.models.pojos.{nombre_simple};
import {base}.repositories.{nombre_simple}Repository;
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
    base = extraer_base_paquete(paquete)
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_var = nombre_simple[0].lower() + nombre_simple[1:]
    return f"""package {base}.services;

import {base}.exceptions.CwsException;
import {base}.models.entities.{nombre_entidad};
import {base}.repositories.{nombre_simple}Repository;
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
    base = extraer_base_paquete(paquete)
    nombre_simple = nombre_entidad.replace("Entity", "")
    nombre_var = nombre_simple[0].lower() + nombre_simple[1:]
    return f"""package {base}.services;

import {base}.mappers.{nombre_simple}Mapper;
import {base}.models.entities.{nombre_entidad};
import {base}.models.pojos.{nombre_simple};
import {base}.repositories.{nombre_simple}Repository;
import {base}.services.Find{nombre_simple}Service;
import {base}.utils.PatchUtils;
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
    base = extraer_base_paquete(paquete)
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {base}.services;

import {base}.models.entities.{nombre_entidad};
import {base}.repositories.{nombre_simple}Repository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class Delete{nombre_simple}Service {{
    private final Find{nombre_simple}Service service;
    private final {nombre_simple}Repository repository;

    public void delete(final {id_tipo} id) {{
        final {nombre_entidad} entity = service.find(id);
        repository.delete(entity);
    }}
}}
"""


def generar_search_service(nombre_entidad, paquete):
    base = extraer_base_paquete(paquete)
    nombre_simple = nombre_entidad.replace("Entity", "")
    return f"""package {base}.services;

import {base}.factories.{nombre_simple}SpecificationFactory;
import {base}.mappers.{nombre_simple}Mapper;
import {base}.models.dtos.{nombre_simple}Dto;
import {base}.models.entities.{nombre_entidad};
import {base}.repositories.{nombre_simple}Repository;
import {base}.search.{nombre_simple}SearchModel;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

import java.util.Collection;

@RequiredArgsConstructor
@Service
public class Search{nombre_simple}Service {{
    private final {nombre_simple}Repository repository;

    public Collection<{nombre_simple}Dto> search(final {nombre_simple}SearchModel searchModel, final Pageable pageable) {{
        final Specification<{nombre_entidad}> specification =
                {nombre_simple}SpecificationFactory.mapToSpecification(searchModel);

        return repository.findAll(specification, pageable).map({nombre_simple}Mapper::toDto).getContent();
    }}
}}
"""

