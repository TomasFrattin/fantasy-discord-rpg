from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
import random
from data.texts import SLEEP_DESCS
from utils.messages import mensaje_usuario_no_creado, mensaje_sin_energia, mensaje_accion_en_progreso

async def run_sleep(interaction: Interaction):
    user_id = str(interaction.user.id)

    row = db.obtener_jugador(user_id)
    if not row:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)
    
    energia = db.obtener_energia(user_id)
    if energia <= 0:
        return await interaction.response.send_message(embed=mensaje_sin_energia(), ephemeral=True)
    
    accion = db.obtener_accion_actual(user_id)
    if accion:
        return await interaction.response.send_message(embed=mensaje_accion_en_progreso(user_id), ephemeral=True)

    if row["vida"] >= row["vida_max"]:
        embed = Embed(
            title="🤔 Vida al máximo",
            description="Tu vida ya está completa. ¡No necesitas descansar ahora!",
            color=0xC9A0DC  # lavanda/místico, queda re bien
            )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Gastar energía
    db.gastar_energia(user_id, 1)

    # Realizar recuperación
    nueva_vida, recuperado = db.sleep(user_id)

    # Descripción larga y estética
    texto_flavor = random.choice(SLEEP_DESCS)

    # Crear embed bonito
    embed = Embed(
        title="😴 Descanso reparador",
        description=texto_flavor,
        color=0xC9A0DC  # lavanda/místico, queda re bien
    )

    embed.add_field(
        name="❤️ Vida recuperada",
        value=f"**+{recuperado}**",
        inline=False
    )

    embed.add_field(
        name="💗 Vida actual",
        value=f"**{nueva_vida}**",
        inline=False
    )

    # Lo dejaremos para si en un futuro podemos elegir la cantidad de energía a gastar
    # embed.add_field(
    #     name="🔋 Energía consumida",
    #     value="**1 punto**",
    #     inline=False
    # )

    await interaction.response.send_message(embed=embed, ephemeral=True)


class SleepCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sleep", description="Recuperar 20% de tu vida máxima.")
    async def sleep(self, interaction: Interaction):
        await run_sleep(interaction)

async def setup(bot):
    await bot.add_cog(SleepCommand(bot))
