import discord
from discord import app_commands
from discord.ext import commands

from data_loader import EQUIPABLES_BY_ID
from data.canas import CANAS
from services.jugadores import obtener_jugador
from utils import db
from utils.messages import mensaje_usuario_no_creado
from utils.estado_jugador import formatear_estado_jugador


RARITY_STYLE = {
    "comun": {"emoji": "⚪", "color": 0xA8A8A8},
    "raro": {"emoji": "🔵", "color": 0x4A90E2},
    "poco_comun": {"emoji": "🟢", "color": 0x4CAF50},
    "epico": {"emoji": "🟣", "color": 0x9B59B6},
    "legendario": {"emoji": "🟡", "color": 0xF1C40F},
}

RAREZA_ORDEN = {"legendario": 4, "epico": 3, "raro": 2, "comun": 1}


def formatear_stat_unico(item):
    stats = item.get("stats", {})
    if "ataque" in stats:
        return f" (+{stats['ataque']} ATK)"
    if "vida" in stats:
        return f" (+{stats['vida']} HP)"
    return ""


def formatear_slot(item_id):
    if not item_id:
        return "—"

    item = EQUIPABLES_BY_ID.get(item_id)
    if not item:
        return item_id

    rareza = item.get("rareza", "comun")
    emoji = RARITY_STYLE.get(rareza, RARITY_STYLE["comun"])["emoji"]
    return f"{emoji} {item['nombre']}{formatear_stat_unico(item)}"


def formatear_cana(cana_id):
    if not cana_id:
        return "—"
    cana = CANAS.get(cana_id)
    return f"🎣 {cana['nombre']}" if cana else cana_id


def construir_inventario_embed(user_id: str, categoria="todos"):
    """Construye el embed del inventario filtrado por categoría."""
    row = obtener_jugador(user_id)
    if not row:
        return None

    slots = {
        "🗡 Arma": row["arma_equipada"],
        "🛡 Armadura": row["armadura_equipada"],
        "👑 Casco": row["casco_equipado"],
        "🥾 Botas": row["botas_equipadas"],
        "🎣 Caña": row["cana_equipada"],
    }
    slots_texto = "\n".join(
        f"{emoji}: {formatear_cana(item_id) if emoji == '🎣 Caña' else formatear_slot(item_id)}"
        for emoji, item_id in slots.items()
    )

    inventario = db.obtener_inventario(user_id)
    if categoria == "equipamiento":
        inventario = [
            obj for obj in inventario
            if obj["tipo"] in {"arma", "armadura", "casco", "botas"}
        ]
    elif categoria != "todos":
        inventario = [obj for obj in inventario if obj["tipo"] == categoria]

    inventario.sort(
        key=lambda obj: (
            -RAREZA_ORDEN.get(obj["rareza"], 0),
            obj["nombre"].lower(),
        )
    )
    inventario_texto = "\n".join(
        f"{RARITY_STYLE.get(obj['rareza'], RARITY_STYLE['comun'])['emoji']} "
        f"**{obj['nombre']}** × {obj['cantidad']}"
        for obj in inventario
    ) or "Vacío"

    nombre_categoria = {
        "todos": "📦 Objetos",
        "consumible": "🧪 Consumibles",
        "material": "🪵 Materiales",
        "equipamiento": "⚔️ Equipamiento almacenado",
    }.get(categoria, "📦 Objetos")

    embed = discord.Embed(
        title=f"🎒 Inventario de {row['username']}",
        description=formatear_estado_jugador(row),
        color=0x4CAF50,
    )
    if categoria == "equipamiento":
        embed.add_field(name="🛡️ Set equipado", value=slots_texto, inline=False)
    embed.add_field(name=nombre_categoria, value=inventario_texto, inline=False)
    return embed


async def run_inventory(interaction: discord.Interaction):
    return construir_inventario_embed(str(interaction.user.id))


class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Muestra tu inventario de personaje.")
    async def inventory(self, interaction: discord.Interaction):
        embed = await run_inventory(interaction)
        if not embed:
            return await interaction.response.send_message(
                embed=mensaje_usuario_no_creado(), ephemeral=True
            )

        from views.inventory import InventoryView
        await interaction.response.send_message(
            embed=embed,
            view=InventoryView(str(interaction.user.id)),
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
