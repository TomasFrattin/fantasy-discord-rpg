# from discord import app_commands, Interaction
# from discord.ext import commands
# from utils import db
# from views.menu import AccionesMenu


# class MenuCommand(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @app_commands.command(name="menu", description="Abrir menú de acciones.")
#     async def menu(self, interaction: Interaction):
#         user_id = str(interaction.user.id)

#         row = db.obtener_jugador(user_id)
#         if not row:
#             return await interaction.response.send_message(
#                 "⚠️ No tenés personaje creado. Usá **/start**.",
#                 ephemeral=True
#             )

#         energia = db.obtener_energia(user_id) or 0

#         mensaje = (
#             "🎮 **Menú de Acciones**\n"
#             f"⚡ Energía disponible: **{energia}**\n\n"
#             "Elegí lo que querés hacer:"
#         )

#         view = AccionesMenu(user_id)
#         await interaction.response.send_message(mensaje, view=view, ephemeral=True)


# async def setup(bot):
#     await bot.add_cog(MenuCommand(bot))
