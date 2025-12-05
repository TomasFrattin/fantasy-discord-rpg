# commands/inventario.py
import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from data_loader import EQUIPABLES_BY_ID

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

        def nombre_item(item_id):
            if not item_id:
                return "Nada"
            item = EQUIPABLES_BY_ID.get(item_id)
            return item["nombre"] if item else item_id

        # Slots equipables
        slots = {
            "🗡 Arma": row["arma_equipada"],
            "🛡 Armadura": row["armadura_equipada"],
            "👑 Casco": row["casco_equipado"],
            "🥾 Botas": row["botas_equipadas"]
        }
        slots_texto = "\n".join(f"{emoji}: {nombre_item(item)}" for emoji, item in slots.items())

        # Inventario de consumibles/materiales/crafting
        consumibles_rows = db.obtener_inventario(user_id)
        if consumibles_rows:
            consumibles_texto = ", ".join(
                f"{r['cantidad']}× {r['nombre']}" for r in consumibles_rows
            )
        else:
            consumibles_texto = "Vacío"

        msg = (
            f"💰 Oro: **{row['oro']}**\n\n"
            f"{slots_texto}\n\n"
            f"🎒 Inventario: {consumibles_texto}"
        )

        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
