# Contexto del proyecto: Arkanor

## Propósito y estado

Arkanor es un bot RPG para Discord, escrito en Python con `discord.py`. Está en beta: las mecánicas activas pueden cambiar, pero los comandos publicados se conservan salvo una decisión explícita de ruptura.

- Interfaz de jugador: español rioplatense.
- Código, módulos y campos técnicos: inglés.
- Dependencias principales: `discord.py`, `python-dotenv`, `Pillow` y SQLite estándar.

## Inicio y configuración

- Punto de entrada: `bot.py`.
- Configuración: `config.py`, alimentado desde `.env`.
- Variables: `DISCORD_TOKEN`, `DB_FILE` (por defecto `data/arkanor.db`) y `PREFIX`.
- Comando local: `python bot.py` con el entorno virtual activo.
- Al iniciar, `bot.py` sincroniza tablas, catálogos, dungeons/bosses y carga extensiones de comandos. En `on_ready` inicia tareas, sincroniza slash commands y publica el mensaje de bienvenida en `WELCOME_CHANNELS`.

La base no se elimina en cada arranque. Las inserciones de catálogo y dungeons son idempotentes: crear o reiniciar el bot no debe duplicarlas. Un wipe se realiza manualmente, con el bot apagado, eliminando `data/arkanor.db` y sus archivos WAL/SHM si existen.

## Mapa de carpetas

| Ruta | Responsabilidad |
|---|---|
| `commands/` | Cogs y puntos de entrada de slash commands. |
| `views/` | Botones, modales y vistas interactivas de Discord. |
| `services/` | Reglas de juego y operaciones de dominio. |
| `utils/` | Acceso SQLite, creación de tablas, mensajes, locks, combate e imágenes. |
| `data/` | Base SQLite y catálogos JSON. |
| `assets/` | Imágenes de mobs, peces, NPCs, materiales y equipo. |
| `tasks/` | Loops programados. |

## Comandos publicados

`bot.py` carga: `/start`, `/commands`, `/energy`, `/profile`, `/inventory`, `/sleep`, `/forage`, `/hunt`, `/merchant`, `/fish`, `/u`, `/craft`, `/contribuir`, `/ranking` y `/dungeon`.

`commands/loot.py` no se carga como cog: expone `generar_loot_para_usuario`, reutilizada por cacería. `/u` es un menú alternativo; Hunt y Forage deben invocar las mismas funciones `run_hunt` y `run_forage` que sus slash commands.

## Datos y persistencia

SQLite contiene las tablas `jugadores`, `items`, `inventario`, `fondos`, `contribuciones`, `dungeon` y `boss`.

- `jugadores`: vida, daño, energía, experiencia, oro, afinidad, equipo y estados de acción.
- `items`: catálogo común para cualquier objeto inventariable.
- `inventario`: cantidad por `user_id` e `item_id`.
- Las columnas de equipo en `jugadores` guardan IDs de arma, armadura, casco y botas.

`data/materiales.json` y `data/equipables.json` continúan separados como fuentes de contenido. `utils/tablas.py::crear_tabla_items()` sincroniza ambos en `items`, por lo que el inventario puede hacer JOIN y mostrar materiales y equipables. Los stats de equipo se leen actualmente desde `data_loader.py`, que indexa `equipables.json` por ID, tipo y rareza.

## Flujos principales

| Funcionalidad | Entrada y módulos clave |
|---|---|
| Creación de personaje | `commands/start.py` → `views/affinity.py` → `services/jugadores.py` |
| Inventario y equipo | `commands/inventory.py`, `views/equip.py`, `utils/db.py` |
| Recolección | `commands/forage.py` → `services/recoleccion.py` → `utils/db.py` |
| Cacería | `commands/hunt.py` → `utils/combat_manager.py` / `views/combat.py` → loot |
| Pesca | `commands/fish.py` → `views/fish.py` y `data/canas.py` |
| Mercader | `commands/merchant.py` → `views/merchant.py` / `views/merchant_tools.py` |
| Fondo y ranking | `commands/contribution.py`, `commands/ranking.py`, `services/contribution.py` |
| Dungeons | `commands/dungeon.py` → `views/dungeon.py` → `services/dungeon_run.py` |

## Recursos temporales

`utils/helpers.py` genera PNGs únicos en `data/temp/` para mobs, peces, NPCs y collages. El código que los adjunta debe cerrar `discord.File` y borrar el PNG en `finally`. `data/temp/` está ignorado por Git.

## Tareas y estados

`tasks/tasks.py` ejecuta `reset_diario` cada minuto y aplica el reset cuando el reloj local marca 20:00. El comentario histórico menciona medianoche, pero el comportamiento real es 20:00.

Los estados de acción y cooldown viven en `jugadores.accion_actual` y `jugadores.accion_fin`; el combate activo también mantiene estado temporal en memoria mediante `utils/combat_manager.py`.

## Navegación rápida para nuevas features

- Nuevo slash command: crear cog en `commands/`, agregarlo explícitamente a `bot.py` y actualizar ayuda/contexto si se publica.
- Nuevo botón o modal: usar `views/` y verificar que la interacción solo reciba una respuesta inicial.
- Nuevo material o equipable: editar el JSON correspondiente; el arranque sincroniza el catálogo SQLite.
- Cambio de recompensa, energía, vida o EXP: revisar primero `services/jugadores.py`, `services/recoleccion.py`, `commands/hunt.py` y `utils/db.py` según la mecánica.
- Cambio de esquema SQLite: modificar `utils/tablas.py`; decidir explícitamente si requiere wipe o migración antes de implementarlo.

## Deuda técnica conocida

- Crafting está publicado pero aún es un mensaje de funcionalidad futura.
- Unificar y simplificar los mecanismos de acciones, locks y cooldowns es una mejora pendiente.
- Los nombres de slash commands tienen mezcla histórica de inglés y español; no renombrarlos sin un plan de transición.
