from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
import random
from data.texts import ENERGY_DESCS
from utils.messages import mensaje_usuario_no_creado

async def run_energy(interaction: Interaction):
    user_id = str(interaction.user.id)
    
    row = db.obtener_jugador(user_id)
    if not row:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

    energia = db.obtener_energia(user_id)
    if energia >= 3:
        desc = random.choice(ENERGY_DESCS["high"])
    elif energia == 2:
        desc = random.choice(ENERGY_DESCS["mid"])
    elif energia == 1:
        desc = random.choice(ENERGY_DESCS["low"])
    else:
        desc = random.choice(ENERGY_DESCS["zero"])

    # Embed estilo similar a /recolectar
    embed = Embed(
        title="⚡ Energía Actual",
        description=f"**{energia}** puntos",
        color=0xF7D358
    )

    embed.add_field(
        name="Estado",
        value=desc,
        inline=True
    )            

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

class EnergyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="energy", description="Muestra tu energía actual.")
    async def energy(self, interaction: Interaction):
        await run_energy(interaction)

async def setup(bot):
    await bot.add_cog(EnergyCommand(bot))
