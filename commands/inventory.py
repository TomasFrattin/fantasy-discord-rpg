# commands/inventario.py
import json
import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from data_loader import ITEMS_BY_ID

class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Muestra tu inventario de personaje.")
    async def inventory(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        row = db.obtener_jugador(user_id)

        if not row:
            return await interaction.response.send_message(
                f"⚠️ No tenés personaje. Usá **/start**.",
                ephemeral=True
            )

        def nombre_item(item_id):
            if not item_id:
                return "Nada"
            item = ITEMS_BY_ID.get(item_id)
            return item["nombre"] if item else item_id

        arma = nombre_item(row["arma_equipada"])
        armadura = nombre_item(row["armadura_equipada"])
        casco = nombre_item(row["casco_equipado"])
        botas = nombre_item(row["botas_equipadas"])

        inv_raw = json.loads(row["inventario"]) if row["inventario"] else []
        consumibles = [ITEMS_BY_ID.get(i, {"nombre": i})["nombre"] for i in inv_raw]
        consumibles_texto = ", ".join(consumibles[:12]) if consumibles else "Vacío"

        msg = (
            f"💰 Oro: **{row['oro']}**\n\n"
            f"🗡 Arma equipada: {arma}\n"
            f"🛡 Armadura equipada: {armadura}\n"
            f"👑 Casco: {casco}\n"
            f"🥾 Botas: {botas}\n\n"
            f"🎒 Consumibles: {consumibles_texto}"
        )

        await interaction.response.send_message(msg)

async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
