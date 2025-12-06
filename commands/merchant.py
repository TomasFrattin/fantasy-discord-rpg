from discord import app_commands, Interaction, Embed
from discord.ext import commands

class MerchantCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="merchant",
        description="Ir a buscar al mercader"
    )
    async def merchant(self, interaction: Interaction):
        embed = Embed(
            title="🏪 Buscando al mercader...",
            description=(
                "Caminás por el mercado esperando encontrar al mercader 🛒, "
                "pero todo está desolado 🏚️. Los puestos vacíos y el silencio te indican "
                "que está en reconstrucción 🔨.\n\n"
                "**¡Pronto podrás comerciar y descubrir nuevas ofertas! 🪙**"
            ),
            color=0xFFA500  # Color naranja
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(MerchantCommand(bot))
