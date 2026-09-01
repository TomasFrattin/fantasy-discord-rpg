# commands/dungeon.py

from discord import app_commands, Interaction, Embed
from discord.ext import commands
from services.jugadores import obtener_jugador
from views.dungeon import DungeonSelectView, dungeon_intro_text

class DungeonCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="dungeon",
        description="Iniciar una dungeon en grupo (máx 4 jugadores)"
    )
    async def dungeon(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        user = obtener_jugador(user_id)
        if not user:
            await interaction.response.send_message("❌ No estás registrado.", ephemeral=True)
            return

        view = DungeonSelectView(leader_id=user_id)

        embed = Embed(
            title="🏰 Viejas ruinas han sido avistadas",
            description=dungeon_intro_text(view.dungeons),
            color=0xFFD700
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        view.message = await interaction.original_response()

# ✅ setup al nivel superior
async def setup(bot):
    await bot.add_cog(DungeonCommand(bot))


# async def run_dungeon(interaction: Interaction):
#     """Función independiente que contiene la lógica base del dungeon."""
#     user_id = str(interaction.user.id)

#     row = obtener_jugador(user_id)
#     if not row:
#         return await interaction.response.send_message(
#             embed=mensaje_usuario_no_creado(),
#             ephemeral=True
#         )

#     accion = obtener_accion_actual(user_id)
#     if accion:
#         return await interaction.response.send_message(
#             embed=mensaje_accion_en_progreso(user_id),
#             ephemeral=True
#         )

#     embed = Embed(
#         title="🗝️ Ecos de una mazmorra olvidada...",
#         description=(
#             "Un susurro lejano atraviesa el silencio 🕯️. "
#             "Las leyendas hablan de mazmorras antiguas, "
#             "pasillos que cambian con cada incursión y horrores "
#             "que castigan a quienes se aventuran sin preparación...\n\n"
#             "Entre murmullos, escuchás una advertencia repetirse:\n"
#             "*nadie que haya entrado solo regresó ileso* ⚠️.\n\n"
#             "Quizá debas conocer a otros aventureros, "
#             "forjar alianzas y reunir un grupo digno antes de "
#             "cruzar esas puertas selladas 🧩⚔️.\n\n"
#             "**Las mazmorras pondrán a prueba algo más que tu fuerza.**"
#         ),
#         color=0x2C2F33
#     )

#     await interaction.response.send_message(embed=embed, ephemeral=True)


# class DungeonCommand(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @app_commands.command(
#         name="dungeon",
#         description="Adentrarse en antiguas mazmorras llenas de peligros y recompensas"
#     )
#     async def dungeon(self, interaction: Interaction):
#         await run_dungeon(interaction)


# async def setup(bot):
#     await bot.add_cog(DungeonCommand(bot))
