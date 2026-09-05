# Guía para agentes

Antes de modificar código, leer `PROJECT_CONTEXT.md` y después abrir solamente los módulos vinculados a la funcionalidad solicitada.

## Reglas de trabajo

- La interfaz de jugador, embeds y documentación se escriben en español rioplatense. El código técnico usa inglés.
- No exponer, registrar ni modificar secretos de `.env`.
- No borrar ni reemplazar `data/arkanor.db` sin una solicitud explícita. Para un wipe, el bot debe estar apagado.
- Preservar cambios locales ajenos; revisar `git status` antes de editar.
- Los slash commands existentes se mantienen durante la beta. Avisar antes de renombrar uno.
- Un flujo accesible desde un slash command y desde `/u` debe reutilizar una función `run_*`; no duplicar su lógica.
- Todo archivo generado en `data/temp/` debe cerrarse y eliminarse después de adjuntarlo a Discord.
- `materiales.json` y `equipables.json` son las fuentes de contenido. La tabla SQLite `items` es el catálogo común que consume el inventario.

## Verificación y documentación

- Ejecutar la verificación más pequeña que cubra el cambio; no iniciar el bot ni modificar datos reales solo para inspeccionar código.
- Actualizar `PROJECT_CONTEXT.md` si cambia la arquitectura, el flujo de datos, las convenciones, el arranque o los comandos publicados.
- Actualizar `README.md` solo si cambia la instalación, configuración o uso por parte de una persona.
