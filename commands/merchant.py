# commands/merchant.py
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from utils.messages import mensaje_usuario_no_creado, mensaje_accion_en_progreso
from services.jugadores import obtener_jugador
from services.acciones import obtener_accion_actual

# -------------------------
# Función independiente
# -------------------------
async def run_merchant(interaction: Interaction):
    user_id = str(interaction.user.id)

    row = obtener_jugador(user_id)
    if not row:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

    accion = obtener_accion_actual(user_id)
    if accion:
        return await interaction.response.send_message(embed=mensaje_accion_en_progreso(user_id), ephemeral=True)
        
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


# -------------------------
# Cog para el comando
# -------------------------
class MerchantCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="merchant",
        description="Ir a buscar al mercader"
    )
    async def merchant(self, interaction: Interaction):
        await run_merchant(interaction)


# -------------------------
# Setup
# -------------------------
async def setup(bot):
    await bot.add_cog(MerchantCommand(bot))
