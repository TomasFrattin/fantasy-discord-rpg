# commands/perfil.py
import json
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
                f"⚠️ No tenés personaje. Usá **/start**.",
                ephemeral=True
            )

        msg = (
            f"📜 **Perfil de {row['username']}**\n"
            f"🔮 Afinidad: **{row['afinidad']}**\n"
            f"⚡ Energía: {row['energia']}\n"
            f"💰 Oro: {row['oro']}\n"
            f"❤️ Vida total: {row['vida']}\n"
            f"⚔️ Daño total: {row['damage']}\n"
            f"🧭 Exploración: {row['exploracion']}\n"
            f"⚔️ Combate: {row['combate']}\n"
            f"🏹 Cacería: {row['caceria']}\n"
        )

        await interaction.response.send_message(msg)

async def setup(bot):
    await bot.add_cog(ProfileCommand(bot))
