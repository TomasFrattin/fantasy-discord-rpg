# Arkanor Bot

Bot RPG para Discord desarrollado con Python y `discord.py`.

## Requisitos

- Python 3.13 o superior.
- Una aplicación de bot en el [portal de desarrolladores de Discord](https://discord.com/developers/applications).
- Un token de bot y el intent privilegiado **Message Content** habilitado.

## Instalación en Windows

Desde la carpeta del proyecto:

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto:

```env
DISCORD_TOKEN=tu_token_del_bot
DB_FILE=data/arkanor.db
PREFIX=!
```

El token es secreto: no debe compartirse ni subirse a Git. La base SQLite guarda el progreso de los jugadores; hacer una copia de `data/arkanor.db` antes de cambios importantes.

## Ejecución

```powershell
python bot.py
```

Al iniciar, el bot crea las tablas faltantes, carga los comandos y sincroniza los slash commands.

## Convenciones del proyecto

- La experiencia de jugador (mensajes, embeds, descripciones y documentación) está en español rioplatense.
- El código técnico (módulos, funciones, clases, campos de base de datos) se mantiene en inglés.
- Los slash commands existentes se conservan para no romper pruebas en beta. Para comandos nuevos se prefiere inglés y nombres cortos; cualquier renombre debe mantener una transición explícita.
- `commands/` expone los cogs y recibe interacciones; `views/` contiene componentes UI; `services/` concentra reglas de negocio; `utils/` contiene acceso SQLite y helpers transversales.

## Desarrollo

`data/` contiene la base SQLite y los catálogos JSON. `assets/` contiene imágenes de juego. Las imágenes generadas durante una interacción se escriben temporalmente en `data/temp/` con nombres únicos y se eliminan tras enviarse.
