# commands/inventario.py
import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from data_loader import EQUIPABLES_BY_ID

# Rareza → emoji + color sugerido
RARITY_STYLE = {
    "comun":       {"emoji": "⚪", "color": 0xA8A8A8},
    "raro":        {"emoji": "🔵", "color": 0x4A90E2},
    "epico":       {"emoji": "🟣", "color": 0x9B59B6},
    "legendario":  {"emoji": "🟡", "color": 0xF1C40F},
}

class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Muestra tu inventario de personaje.")
    async def inventory(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        row = db.obtener_jugador(user_id)

        if not row:
            return await interaction.response.send_message(
                "⚠️ No tenés personaje. Usá **/start**.",
                ephemeral=True
            )

        # -------------------------
        # FUNCIONES AUXILIARES
        # -------------------------

        def formatear_stat_unico(item):
            stats = item.get("stats", {})
            if not stats:
                return ""

            if "ataque" in stats:
                return f" (**+{stats['ataque']} ATK**)"
            if "vida" in stats:
                return f" (**+{stats['vida']} HP**)"
            return ""

        def formatear_slot(item_id):
            if not item_id:
                return "—"

            item = EQUIPABLES_BY_ID.get(item_id)
            if not item:
                return item_id  # fallback raro pero seguro

            bonus = formatear_stat_unico(item)

            rareza = item.get("rareza", "comun")
            emoji = RARITY_STYLE.get(rareza, RARITY_STYLE["comun"])["emoji"]

            return f"{emoji} {item['nombre']}{bonus}"

        # -------------------------
        # SLOTS EQUIPADOS
        # -------------------------

        slots = {
            "🗡 Arma": row["arma_equipada"],
            "🛡 Armadura": row["armadura_equipada"],
            "👑 Casco": row["casco_equipado"],
            "🥾 Botas": row["botas_equipadas"]
        }

        slots_texto = "\n".join(
            f"{emoji}: {formatear_slot(item_id)}"
            for emoji, item_id in slots.items()
        )

        # -------------------------
        # INVENTARIO
        # -------------------------

        inventario = db.obtener_inventario(user_id)

        if inventario:
            inv_lindo = []
            for obj in inventario:
                rareza = obj["rareza"]
                emoji = RARITY_STYLE.get(rareza, RARITY_STYLE["comun"])["emoji"]

                inv_lindo.append(
                    f"{emoji} **{obj['nombre']}** × {obj['cantidad']}"
                )

            inventario_texto = "\n".join(inv_lindo)
        else:
            inventario_texto = "Vacío"

        # -------------------------
        # EMBED FINAL
        # -------------------------

        embed = discord.Embed(
            title="🎒 Inventario de tu personaje",
            description=f"💰 **Oro:** {row['oro']}",
            color=0x4CAF50
        )

        embed.add_field(name="⚔️ Equipo", value=slots_texto, inline=False)
        embed.add_field(name="📦 Objetos", value=inventario_texto, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
