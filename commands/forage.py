from discord import app_commands, Interaction
from discord.ext import commands
from utils import db
from data.texts import RECOLECTAR_DESCRIPTIONS
import random
from discord import Embed
from utils.messages import mensaje_usuario_no_creado, mensaje_sin_energia

class ForageCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="forage", description="Gastas 1 energía y recolectás materiales.")
    async def forage(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        row = db.obtener_jugador(user_id)
        if not row:
            return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)
        energia = db.obtener_energia(user_id)
        if energia <= 0:
            return await interaction.response.send_message(embed=mensaje_sin_energia(), ephemeral=True)

        db.gastar_energia(user_id, 1)

        try:
            resultados = db.recolectar_materiales(user_id)
            texto_flavor = random.choice(RECOLECTAR_DESCRIPTIONS)

            # --- Agrupar duplicados ---
            agrupados = {}
            for item_id, nombre, cantidad in resultados:
                if item_id not in agrupados:
                    agrupados[item_id] = {"nombre": nombre, "cantidad": 0}
                agrupados[item_id]["cantidad"] += cantidad

            # Crear embed
            embed = Embed(
                title="🧺 Recolección completada",
                description=texto_flavor,
                color=0x00ff00
            )

            # Agregar items finales ya sumados
            for info in agrupados.values():
                embed.add_field(
                    name=info["nombre"],
                    value=f"Cantidad: × {info['cantidad']}",
                    inline=True
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[FORAGE] ERROR: {e}")
            await interaction.response.send_message(
                "⚠️ Ocurrió un error durante la recolección.", ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ForageCommand(bot))
