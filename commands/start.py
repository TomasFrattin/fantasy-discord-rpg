from discord import app_commands, Interaction
from discord.ext import commands
from data.texts import WELCOME_MESSAGE
from views.affinity import ElegirAfinidad
from utils import db
from utils.locks import esta_ocupado, comenzar_accion
from utils.messages import mensaje_usuario_ya_existente
from services.jugador import obtener_jugador

class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="start",
        description="Crear tu personaje y elegir tu afinidad."
    )
    async def start(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        # Verificar si está ocupado
        if esta_ocupado(user_id):
            return await interaction.response.send_message(
                "⚠️ Tenés una acción pendiente. Terminá eso primero.",
                ephemeral=True
            )

        # Verificar si ya tiene personaje
        row = obtener_jugador(user_id)
        if row:
            return await interaction.response.send_message(embed=mensaje_usuario_ya_existente(), ephemeral=True)

        # Bloquear
        comenzar_accion(user_id)
        view = ElegirAfinidad(user_id)

        await interaction.response.send_message(
            content=WELCOME_MESSAGE,
            view=view,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(StartCommand(bot))
