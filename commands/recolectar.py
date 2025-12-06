from discord import app_commands, Interaction
from discord.ext import commands
from utils import db
from data.texts import RECOLECTAR_DESCRIPTIONS
import random
from discord import Embed

class RecolectarCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="recolectar", description="Gastas 1 energía y recolectás materiales.")
    async def recolectar(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        energia = db.obtener_energia(user_id)
        if energia is None:
            return await interaction.response.send_message("⚠️ No tenés personaje. Usá /start", ephemeral=True)
        if energia <= 0:
            return await interaction.response.send_message("⚠️ No te queda energía.", ephemeral=True)

        db.gastar_energia(user_id, 1)

        try:
            resultados = db.recolectar_materiales(user_id)
            texto_flavor = random.choice(RECOLECTAR_DESCRIPTIONS)

            # Crear embed
            embed = Embed(
                title="🧺 Recolección completada",
                description=texto_flavor,
                color=0x00ff00
            )

            # Agregar los items encontrados
            for _, nombre, cantidad in resultados:
                embed.add_field(
                    name=f"{nombre}",
                    value=f"Cantidad: × {cantidad} ",
                    inline=True
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[RECOLECTAR] ERROR: {e}")
            await interaction.response.send_message(
                "⚠️ Ocurrió un error durante la recolección.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(RecolectarCommand(bot))
