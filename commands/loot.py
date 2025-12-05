# commands/loot.py
import random
import json
import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from data_loader import ITEMS, ITEMS_BY_ID
from views.equip import EquiparOVender

RARITY_COLORS = {
    "comun": 0xB0B0B0,
    "raro": 0x3A82F7,
    "epico": 0xA335EE,
    "legendario": 0xFF8000
}

ITEMS_BY_RARITY = {}
for item in ITEMS:
    r = item.get("rareza", "comun")
    ITEMS_BY_RARITY.setdefault(r, []).append(item)

def obtener_tier():
    prob = random.random()
    if prob < 0.60: return "comun"
    if prob < 0.85: return "raro"
    if prob < 0.97: return "epico"
    return "legendario"


class LootCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loot", description="Consume energía para obtener un ítem aleatorio.")
    async def loot(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        energia = db.obtener_energia(user_id)

        if energia is None:
            return await interaction.response.send_message("No tenés personaje.", ephemeral=True)
        if energia <= 0:
            return await interaction.response.send_message("⚠️ No te queda energía.", ephemeral=True)

        db.gastar_energia(user_id, 1)

        tier = obtener_tier()
        item = random.choice(ITEMS_BY_RARITY[tier])
        tipo = item.get("tipo", "otro")
        jugador = db.obtener_jugador(user_id)

        # Consumible → no equipable
        if tipo not in ("arma", "armadura", "casco", "botas"):
            db.agregar_consumible(user_id, item["id"])

            embed = discord.Embed(
                title=item["nombre"],
                description=f"Tipo: **{tipo}**\nRareza: **{tier.capitalize()}**",
                color=RARITY_COLORS[tier]
            )
            embed.set_footer(text=f"Energía restante: {db.obtener_energia(user_id)}")

            return await interaction.response.send_message(embed=embed)

        # Equipable
        columnas = {
            "arma": "arma_equipada",
            "armadura": "armadura_equipada",
            "casco": "casco_equipado",
            "botas": "botas_equipadas"
        }
        columna_equipo = columnas[tipo]
        equipada_id = jugador[columna_equipo]

        nuevo_atk = item.get("stats", {}).get("ataque", 0)
        nuevo_hp  = item.get("stats", {}).get("vida", 0)

        embed = discord.Embed(
            title=item["nombre"],
            color=RARITY_COLORS[tier]
        )
        embed.add_field(name="Rareza", value=tier.capitalize(), inline=False)

        if not equipada_id:
            if nuevo_atk: embed.add_field(name="Daño (nuevo)", value=f"+{nuevo_atk}")
            if nuevo_hp:  embed.add_field(name="Vida (nuevo)", value=f"+{nuevo_hp}")
            embed.set_footer(text="No tenés nada equipado de este tipo.")

            view = EquiparOVender(user_id, item, slot_col=columna_equipo)
            return await interaction.response.send_message(embed=embed, view=view)

        equipado = ITEMS_BY_ID.get(equipada_id)
        actual_atk = equipado.get("stats", {}).get("ataque", 0)
        actual_hp  = equipado.get("stats", {}).get("vida", 0)

        embed.add_field(name="Daño", value=f"Nuevo: {nuevo_atk} | Actual: {actual_atk}", inline=False)
        embed.add_field(name="Vida", value=f"Nuevo: {nuevo_hp} | Actual: {actual_hp}", inline=False)
        embed.add_field(name="Equipado actualmente", value=equipado["nombre"], inline=False)

        view = EquiparOVender(user_id, item, slot_col=columna_equipo)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LootCommand(bot))
