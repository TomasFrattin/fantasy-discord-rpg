# commands/merchant.py
from discord import app_commands, Interaction
from discord.ext import commands
from services.jugadores import obtener_jugador
from utils.messages import mensaje_usuario_no_creado
from views.merchant import mostrar_mercader  # nuestra nueva vista
from services.acciones import obtener_accion_actual
from utils.messages import mensaje_accion_en_progreso
from discord import Embed
# -------------------------
# Función independiente (para /menu)
# -------------------------

async def run_merchant(interaction: Interaction):
    user_id = str(interaction.user.id)

    # Verificamos si el jugador existe
    jugador = obtener_jugador(user_id)
    if not jugador:
        return await interaction.response.send_message(
            embed=mensaje_usuario_no_creado(),
            ephemeral=True
        )

    # Verificamos si hay acción en progreso
    accion = obtener_accion_actual(user_id)
    if accion:
        return await interaction.response.send_message(
            embed=mensaje_accion_en_progreso(user_id),
            ephemeral=True
        )

    # Mostramos al mercader
    await mostrar_mercader(interaction)


# -------------------------
# Cog para el comando /merchant
# -------------------------
class MerchantCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="merchant",
        description="Ir a buscar al mercader"
    )
    async def merchant(self, interaction: Interaction):
        await run_merchant(interaction)  # Reutilizamos la función independiente


# -------------------------
# Setup
# -------------------------
async def setup(bot):
    await bot.add_cog(MerchantCommand(bot))
