# commands/ranking.py
import discord
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
from services.ranking import ranking_fondo_visual
from services.contribution import FONDO_MERCHANT, barra_progreso

MEDALLAS = ["🥇", "🥈", "🥉"]

class RankingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ranking",
        description="Muestra el ranking de jugadores que más contribuyeron al merchant"
    )
    async def ranking(self, interaction: Interaction):
        ranking, total_actual, total_objetivo = ranking_fondo_visual(FONDO_MERCHANT, top=10)

        if not ranking:
            return await interaction.response.send_message(
                "Todavía no hay contribuciones al fondo.", ephemeral=True
            )

        embed = Embed(
            title="🏆 Ranking de contribuciones al merchant",
            description=f"Top {len(ranking)} jugadores que aportaron oro",
            color=Color.gold()
        )

        for i, jugador in enumerate(ranking):
            medalla = MEDALLAS[i] if i < 3 else f"{i+1}."
            barra, porcentaje = barra_progreso(jugador["cantidad"], total_objetivo)
            embed.add_field(
                name=f"{medalla} {jugador['username']}",
                value=(
                    f"Oro aportado: {jugador['cantidad']} ({jugador['porcentaje_objetivo']}% del objetivo)\n"
                    f"{barra} {porcentaje}% del objetivo"
                ),
                inline=False
            )

        embed.set_footer(text=f"**Total acumulado: {total_actual}/{total_objetivo} de oro**")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(RankingCommand(bot))
