# commands/profile.py
import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from utils.messages import mensaje_usuario_no_creado

async def run_profile(interaction: Interaction):
    user_id = str(interaction.user.id)
    
    row = db.obtener_jugador(user_id)
    if not row:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)
    
    # --------------------------
    # EMBED DEL PERFIL
    # --------------------------
    embed = discord.Embed(
        title=f"📜 Perfil de {row['username']}",
        color=0x1ABC9C
    )

    # ----- Vida -----
    vida_actual = row["vida"]
    vida_max = row["vida_max"]

    embed.add_field(
        name="❤️ Vida",
        value=f"**{vida_actual} / {vida_max}**",
        inline=True
    )

    # ----- Daño -----
    embed.add_field(
        name="⚔️ Daño",
        value=f"**{row['damage']}**",
        inline=True
    )

    # ----- Afinidad -----
    embed.add_field(
        name="🔮 Afinidad",
        value=f"**{row['afinidad']}**",
        inline=False
    )

    # ----- Progresión -----
    lvl_c = row["lvl_caceria"]
    exp_c = row["exp_caceria"]
    exp_c_needed = int(150 * (lvl_c ** 1.3))

    lvl_r = row["lvl_recoleccion"]
    exp_r = row["exp_recoleccion"]
    exp_r_needed = int(150 * (lvl_r ** 1.3))

    lvl_p = row["lvl_prestigio"]

    embed.add_field(
        name="📈 Progresión",
        value=(
            f"🏹 **Cacería**\n"
            f"   Nivel: **{lvl_c}**\n"
            f"   EXP: **{exp_c} / {exp_c_needed}**\n\n"

            f"🌿 **Recolección**\n"
            f"   Nivel: **{lvl_r}**\n"
            f"   EXP: **{exp_r} / {exp_r_needed}**\n\n"

            f"✨ **Prestigio**\n"
            f"   Nivel: **{lvl_p}**"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)


class ProfileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Muestra tu perfil de personaje.")
    async def profile(self, interaction: discord.Interaction):
        await run_profile(interaction)

async def setup(bot):
    await bot.add_cog(ProfileCommand(bot))
