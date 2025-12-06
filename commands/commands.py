from discord import app_commands, Interaction, Embed
from discord.ext import commands
from data.texts import STARTUP_COMMANDS

class CommandsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="commands", description="Lista todos los comandos disponibles del bot.")
    async def commands(self, interaction: Interaction):
        embed = Embed(
            title="📜 Comandos de Arkanor",
            description="Guía rápida de tus comandos disponibles:",
            color=0x1ABC9C
        )

        for cmd in STARTUP_COMMANDS:
            embed.add_field(
                name=f"**{cmd['comando']}**",
                value=cmd['descripcion'],
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CommandsCommand(bot))
