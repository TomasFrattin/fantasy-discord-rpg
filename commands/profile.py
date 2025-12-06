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
            description=f"🔮 **Afinidad:** {row['afinidad']}",
            color=0x9B59B6
        )

        # Stats principales
        embed.add_field(
            name="⚔️ Daño total",
            value=f"**{row['damage']}**",
            inline=True
        )
        embed.add_field(
            name="❤️ Vida total",
            value=f"**{row['vida']}**",
            inline=True
        )

        # Progresión
        progreso = (
            f"🧭 Exploración: **{row['exploracion']}**\n"
            f"⚔️ Combate: **{row['combate']}**\n"
            f"🏹 Cacería: **{row['caceria']}**"
        )

        embed.add_field(
            name="📈 Progresión",
            value=progreso,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCommand(bot))
