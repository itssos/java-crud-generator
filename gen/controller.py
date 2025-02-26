def generar_get_controller(nombre_entidad, paquete):
    """
    Controller que maneja GET /entities/{id}
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    return f"""package {paquete}.controllers;

import org.springframework.web.bind.annotation.*;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.services.Find{nombre_simple}Service;

@RestController
public class Get{nombre_simple}Controller {{

    private final Find{nombre_simple}Service findService;

    public Get{nombre_simple}Controller(Find{nombre_simple}Service findService) {{
        this.findService = findService;
    }}

    @GetMapping("/{ruta}/{{id}}")
    public {nombre_entidad} findById(@PathVariable Long id) {{
        return findService.findById(id);
    }}
}}
"""

def generar_post_controller(nombre_entidad, paquete):
    """
    Controller que maneja POST /entities
    """
    nombre_simple = nombre_entidad.replace("Entity", "")
    ruta = nombre_simple.lower() + "s"
    return f"""package {paquete}.controllers;

import org.springframework.web.bind.annotation.*;
import {paquete}.models.entities.{nombre_entidad};
import {paquete}.services.Create{nombre_simple}Service;

@RestController
public class Post{nombre_simple}Controller {{

    private final Create{nombre_simple}Service createService;

    public Post{nombre_simple}Controller(Create{nombre_simple}Service createService) {{
        this.createService = createService;
    }}

    @PostMapping("/{ruta}")
    public {nombre_entidad} create(@RequestBody {nombre_entidad} entity) {{
        return createService.create(entity);
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