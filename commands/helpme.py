from discord import app_commands, Interaction
from discord.ext import commands
from discord import Embed

class HelpmeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="helpme", description="Lista todos los comandos disponibles del bot.")
    async def helpme(self, interaction: Interaction):
        embed = Embed(title="🌌 Comandos de Arkanor Bot", color=0x8A2BE2)
        embed.add_field(name="/start", value="Crear tu personaje y elegir tu afinidad.", inline=False)
        embed.add_field(name="/perfil", value="Mostrar tu perfil completo.", inline=False)
        embed.add_field(name="/inventario", value="Revisar tu inventario y equipamiento.", inline=False)
        embed.add_field(name="/energia", value="Consultar tu energía.", inline=False)
        embed.add_field(name="/loot", value="Buscar tesoros y objetos.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpmeCommand(bot))
