from discord import app_commands, Interaction
from discord.ext import commands
from utils import db

class RecolectarCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="recolectar", description="Gastas 1 energía y recolectás materiales.")
    async def recolectar(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        # Verificar energía
        energia = db.obtener_energia(user_id)
        if energia is None:
            return await interaction.response.send_message(
                "⚠️ No tenés personaje. Usá /start", ephemeral=True
            )
        if energia <= 0:
            return await interaction.response.send_message(
                "⚠️ No te queda energía.", ephemeral=True
            )

        # Gastar energía
        db.gastar_energia(user_id, 1)

        # Ejecutar recolección
        try:
            _, texto = db.recolectar_materiales(user_id)
            await interaction.response.send_message(texto, ephemeral=True)
        except Exception as e:
            print(f"[RECOLECTAR] ERROR: {e}")
            await interaction.response.send_message(
                "⚠️ Ocurrió un error durante la recolección.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(RecolectarCommand(bot))
