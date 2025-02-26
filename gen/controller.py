def generar_get_controller(nombre_entidad, paquete):
    """
    Controller que maneja GET /1.0/<ruta> con paginación y un modelo de búsqueda.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    return f"""package {paquete}.controllers;

import {paquete}.models.dtos.{nombre_simple}Dto;
import {paquete}.search.{nombre_simple}SearchModel;
import {paquete}.services.Search{nombre_simple}Service;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collection;

@RequiredArgsConstructor
@RestController
@RequestMapping("/1.0/{ruta}")
public class Get{nombre_simple}Controller {{

    private final Search{nombre_simple}Service service;

    @GetMapping
    public ResponseEntity<Collection<{nombre_simple}Dto>> get(final {nombre_simple}SearchModel searchModel,
                                                              final Pageable pageable) {{
        return ResponseEntity.ok(service.search(searchModel, pageable));
    }}
}}
"""

def generar_post_controller(nombre_entidad, paquete):
    """
    Controller que maneja POST /1.0/<ruta>,
    usando un DTO, un POJO, anotaciones de auditoría, etc.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    # Para usar en la constante estática (por ejemplo CON_PATIENT -> CON_PATIENT)
    nombre_simple_upper = nombre_simple.upper()

    return f"""package {paquete}.controllers;

import {paquete}.annotations.Audit;
import {paquete}.enums.AuditAction;
import {paquete}.models.dtos.{nombre_simple}Dto;
import {paquete}.models.pojos.{nombre_simple};
import {paquete}.services.Create{nombre_simple}Service;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RequiredArgsConstructor
@RestController
@RequestMapping("/1.0/{ruta}")
public class Post{nombre_simple}Controller {{
    private static final long CON_{nombre_simple_upper} = 40; // Ajusta el valor según tu necesidad

    private final Create{nombre_simple}Service service;

    @Audit(controllerId = CON_{nombre_simple_upper}, action = AuditAction.POST)
    @PostMapping
    public ResponseEntity<{nombre_simple}Dto> create(@Valid @RequestBody {nombre_simple} newObject) {{
        return new ResponseEntity<>(service.create(newObject), HttpStatus.CREATED);
    }}
}}
"""

def generar_patch_controller(nombre_entidad, paquete):
    """
    Controller que maneja PATCH /1.0/<ruta> usando auditoría, RequiredArgsConstructor y respuesta sin contenido.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    # Nombre en mayúsculas para la constante (e.g. "PATIENT")
    nombre_simple_upper = nombre_simple.upper()
    # Variable para el identificador en el path (e.g. "patient" de "Patient")
    nombre_var = nombre_simple[0].lower() + nombre_simple[1:]
    
    return f"""package {paquete}.controllers;

import {paquete}.annotations.Audit;
import {paquete}.enums.AuditAction;
import {paquete}.models.pojos.{nombre_simple};
import {paquete}.services.Patch{nombre_simple}Service;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RequiredArgsConstructor
@RestController
@RequestMapping("/1.0/{ruta}")
public class Patch{nombre_simple}Controller {{
    private static final long CON_{nombre_simple_upper} = 40;
    private final Patch{nombre_simple}Service service;

    @Audit(controllerId = CON_{nombre_simple_upper}, action = AuditAction.PATCH)
    @PatchMapping("/{{{nombre_var}Id}}")
    public ResponseEntity<Void> patch(@PathVariable final Long {nombre_var}Id, @RequestBody final {nombre_simple} {nombre_var}) {{
        service.patch({nombre_var}Id, {nombre_var});
        return ResponseEntity.noContent().build();
    }}
}}
"""

def generar_delete_controller(nombre_entidad, paquete):
    """
    Controller que maneja DELETE /1.0/<ruta> usando auditoría y devuelve ResponseEntity sin contenido.
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    nombre_simple_upper = nombre_simple.upper()
    nombre_var = nombre_simple[0].lower() + nombre_simple[1:]
    
    return f"""package {paquete}.controllers;

import {paquete}.annotations.Audit;
import {paquete}.enums.AuditAction;
import {paquete}.services.Delete{nombre_simple}Service;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RequiredArgsConstructor
@RestController
@RequestMapping("/1.0/{ruta}")
public class Delete{nombre_simple}Controller {{
    private static final long CON_{nombre_simple_upper} = 40;
    private final Delete{nombre_simple}Service service;

    @Audit(controllerId = CON_{nombre_simple_upper}, action = AuditAction.DELETE)
    @DeleteMapping("/{{{nombre_var}Id}}")
    public ResponseEntity<Void> delete(@PathVariable final Long {nombre_var}Id) {{
        service.delete({nombre_var}Id);
        return ResponseEntity.noContent().build();
    }}
}}
"""

def generar_search_controller(nombre_entidad, paquete):
    """
    Controller que maneja GET /entities (búsqueda/listado).
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    return f"""package {paquete}.controllers;

import org.springframework.web.bind.annotation.*;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.services.Search{nombre_simple}Service;
import java.util.List;

@RestController
public class Search{nombre_simple}Controller {{

    private final Search{nombre_simple}Service searchService;

    public Search{nombre_simple}Controller(Search{nombre_simple}Service searchService) {{
        this.searchService = searchService;
    }}

    @GetMapping("/{ruta}")
    public List<{nombre_entidad}> searchAll() {{
        return searchService.searchAll();
    }}
}}
"""