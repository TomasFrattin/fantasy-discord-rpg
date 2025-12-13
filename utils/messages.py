from discord import Embed, Color
from utils import db
from services.acciones import obtener_accion_actual

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


def mensaje_accion_en_progreso(user_id: str):
    accion = obtener_accion_actual(user_id)
    accion_texto = accion if accion else "desconocida"
    
    embed = Embed(
        title="⏳ Acción en progreso",
        description=f"Ya estás realizando la acción `{accion_texto}`. Por favor, finaliza la actual antes de iniciar una nueva.",
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

def mensaje_funcionalidad_en_mantenimiento():
    embed = Embed(
        title="🔧 Funcionalidad en mantenimiento",
        description="Esta funcionalidad está en mantenimiento. Próximamente estará disponible. Disculpe las molestias.",
        color=Color.orange()
    )
    return embed