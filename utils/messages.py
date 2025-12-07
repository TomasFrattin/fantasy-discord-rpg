from discord import Embed, Color

def mensaje_usuario_ya_existente():
    embed = Embed(
        title="⚠️ Personaje existente",
        description="Ya tenés un personaje creado.",
        color=Color.red()
    )
    return embed

def mensaje_usuario_no_creado():
    embed = Embed(
        title="⚠️ Sin personaje",
        description="No tenés un personaje creado. Usá `/start` para crear uno.",
        color=Color.red()
    )
    return embed

def mensaje_sin_energia():
    embed = Embed(
        title="⚠️ Sin energía",
        description="No te queda energía.",
        color=Color.red()
    )
    return embed

def mensaje_accion_en_progreso():
    embed = Embed(
        title="⏳ Acción en progreso",
        description="Ya estás realizando otra acción. Por favor, finaliza la actual antes de iniciar una nueva.",
        color=Color.red()
    )
    return embed

def mensaje_funcionalidad_en_progreso():
    embed = Embed(
        title="⚠️ Funcionalidad en progreso",
        description="Esta funcionalidad está en desarrollo. Próximamente estará disponible.",
        color=Color.orange()
    )
    return embed

def mensaje_accion_caducada():
    embed = Embed(
        title="⌛ Acción caducada",
        description="El tiempo para interactuar con esta acción ha expirado.",
        color=Color.red()
    )
    return embed