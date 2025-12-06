# commands/profile.py
import discord
from discord import app_commands
from discord.ext import commands
from utils import db

class ProfileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Muestra tu perfil de personaje.")
    async def profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        row = db.obtener_jugador(user_id)

        if not row:
            return await interaction.response.send_message(
                "⚠️ No tenés personaje. Usá **/start**.",
                ephemeral=True
            )

        # --------------------------
        # EMBED DEL PERFIL
        # --------------------------
        embed = discord.Embed(
            title=f"📜 Perfil de {row['username']}",
            color=0x1ABC9C
        )

        vida_actual = row["vida"]
        vida_max = row["vida_max"]

        embed.add_field(
            name="❤️ Vida",
            value=f"**{vida_actual} / {vida_max}**",
            inline=True
        )

        embed.add_field(
            name="⚔️ Daño",
            value=f"**{row['damage']}**",
            inline=True
        )

        embed.add_field(
            name="🔮 Afinidad",
            value=f"**{row['afinidad']}**",
            inline=False
        )

        embed.add_field(
            name="📈 Progresión",
            value=(
                # f"🧭 Exploración: **{row['exploracion']}W**\n"
                # f"⚔️ Combate: **{row['combate']}**\n"
                # f"🏹 Cacería: **{row['caceria']}**"
                f"🧭 Exploración: **WIP**\n"
                f"⚔️ Combate: **WIP**\n"
                f"🏹 Cacería: **WIP**"
            ),
            inline=False
        )


        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCommand(bot))
