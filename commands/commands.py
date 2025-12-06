from discord import app_commands, Interaction
from discord.ext import commands
from discord import Embed

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

        embed.add_field(
            name="🧙‍♂️ **/start**",
            value="Creá tu personaje y elegí tu afinidad.",
            inline=False
        )

        embed.add_field(
            name="📚 **/commands**",
            value="Mostrá todos los comandos disponibles.",
            inline=False
        )

        embed.add_field(
            name="🧾 **/perfil**",
            value="Mostrá tu perfil completo.",
            inline=False
        )

        embed.add_field(
            name="🎒 **/inventario**",
            value="Revisá tu inventario y equipamiento.",
            inline=False
        )

        embed.add_field(
            name="⚡ **/energia**",
            value="Consultá tu energía actual.",
            inline=False
        )

        embed.add_field(
            name="🐺 **/hunt**",
            value="Buscá tesoros y objetos valiosos.",
            inline=False
        )

        embed.add_field(
            name="😴 **/sleep**",
            value="Descansá y recuperá energía.",
            inline=False
        )

        embed.add_field(
            name="🧺 **/forage**",
            value="Gastá energía para obtener materiales.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CommandsCommand(bot))
