from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
import random
from data.texts import ENERGY_DESCS

class EnergyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="energy", description="Muestra tu energía actual.")
    async def energy(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        energia = db.obtener_energia(user_id)

        if energia is None:
            return await interaction.response.send_message(
                "⚠️ Aún no tenés personaje. Usá **/start**.",
                ephemeral=True
            )

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


async def setup(bot):
    await bot.add_cog(EnergyCommand(bot))
