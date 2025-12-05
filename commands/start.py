from discord import app_commands, Interaction
from discord.ext import commands
from data.texts import WELCOME_MESSAGE
from views.affinity import ElegirAfinidad
from utils import db

class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="start", description="Crear tu personaje y elegir tu afinidad.")
    async def start(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        row = db.obtener_jugador(user_id)
        if row:
            await interaction.response.send_message(
                "⚠️ Ya tenés un personaje creado.", ephemeral=True
            )
            return

        view = ElegirAfinidad(user_id)
        await interaction.response.send_message(
            content=WELCOME_MESSAGE,
            view=view,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(StartCommand(bot))