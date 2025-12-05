from discord import app_commands, Interaction
from discord.ext import commands
from utils import db


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

        mensaje = (
            "⚡ **Energía Actual**\n"
            f"Tenés **{energia}** puntos de energía."
        )

        await interaction.response.send_message(
            mensaje,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(EnergyCommand(bot))
