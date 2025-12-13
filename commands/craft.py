# commands/craft.py
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from utils.messages import mensaje_usuario_no_creado, mensaje_accion_en_progreso
from services.jugadores import obtener_jugador
from services.acciones import obtener_accion_actual

async def run_craft(interaction: Interaction):
    """Función independiente que contiene la lógica de crafting."""
    user_id = str(interaction.user.id)

    row = obtener_jugador(user_id)
    if not row:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

    accion = obtener_accion_actual(user_id)
    if accion:
        return await interaction.response.send_message(embed=mensaje_accion_en_progreso(user_id), ephemeral=True)
    
    embed = Embed(
        title="🔨 Explorando posibilidades...",
        description=(
            "Observás tu bolsa de materiales rebosante y notas que podrían ser útiles 🧰, "
            "pero no encontrás las herramientas adecuadas para darles forma 🪚. "
            "Quizá pronto logres construir objetos que te ayuden en tus aventuras ✨.\n\n"
            "**¡La creatividad y la paciencia son tus mejores aliadas! 🧙‍♂️**"
        ),
        color=0x8B4513  # Marrón/tono madera
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


class CraftCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="craft",
        description="Intentar crear objetos con tus materiales"
    )
    async def craft(self, interaction: Interaction):
        await run_craft(interaction)


async def setup(bot):
    await bot.add_cog(CraftCommand(bot))
