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
    Controller que maneja PATCH /entities/{id}
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    return f"""package {paquete}.controllers;

import org.springframework.web.bind.annotation.*;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.services.Patch{nombre_simple}Service;

@RestController
public class Patch{nombre_simple}Controller {{

    private final Patch{nombre_simple}Service patchService;

    public Patch{nombre_simple}Controller(Patch{nombre_simple}Service patchService) {{
        this.patchService = patchService;
    }}

    @PatchMapping("/{ruta}/{{id}}")
    public {nombre_entidad} patch(@PathVariable Long id, @RequestBody {nombre_entidad} partialEntity) {{
        return patchService.patch(id, partialEntity);
    }}
}}
"""

def generar_delete_controller(nombre_entidad, paquete):
    """
    Controller que maneja DELETE /entities/{id}
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    return f"""package {paquete}.controllers;

import org.springframework.web.bind.annotation.*;
import {paquete}.services.Delete{nombre_simple}Service;

@RestController
public class Delete{nombre_simple}Controller {{

    private final Delete{nombre_simple}Service deleteService;

    public Delete{nombre_simple}Controller(Delete{nombre_simple}Service deleteService) {{
        this.deleteService = deleteService;
    }}

    @DeleteMapping("/{ruta}/{{id}}")
    public void delete(@PathVariable Long id) {{
        deleteService.delete(id);
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