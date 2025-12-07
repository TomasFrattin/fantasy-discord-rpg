# commands/fish.py
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from utils.messages import mensaje_usuario_no_creado

async def run_fish(interaction: Interaction):
    """Función independiente que contiene la lógica de pescar."""
    user_id = str(interaction.user.id)
    row = db.obtener_jugador(user_id)
    if not row:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

    embed = Embed(
        title="🌊 Aguas inestables...",
        description=(
            "Te acercás a la orilla para ver si podés pescar algo, "
            "pero las tormentas dejaron el agua demasiado turbulenta 🌪️ y no tenés ninguna caña 🎣❌.\n\n"
            "**¡Pronto podrás pescar y descubrir los secretos del océano! 🌟**"
        ),
        color=0x3BA3F2
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


class FishingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="fish",
        description="Intentar pescar en las aguas del reino"
    )
    async def fish(self, interaction: Interaction):
        await run_fish(interaction)


async def setup(bot):
    await bot.add_cog(FishingCommand(bot))
