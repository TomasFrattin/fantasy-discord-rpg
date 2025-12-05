# import discord
# from discord.ui import View, Button
# from utils import db


# class AccionesMenu(View):
#     def __init__(self, user_id: str):
#         super().__init__(timeout=60)
#         self.user_id = user_id

#         # Botones deshabilitados
#         self.add_item(Button(label="Expediciones (WIP)", style=2, disabled=True))
#         self.add_item(Button(label="Duelos (WIP)", style=2, disabled=True))

#     async def interaction_check(self, interaction: discord.Interaction):
#         return str(interaction.user.id) == self.user_id

#     @discord.ui.button(label="sleep", style=discord.ButtonStyle.primary)
#     async def sleep(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message(
#             "😴 Descansando... (WIP, usar /sleep por ahora)",
#             ephemeral=True
#         )

#     @discord.ui.button(label="Explorar Zona", style=discord.ButtonStyle.primary)
#     async def explorar(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message(
#             "🌲 Explorás una zona desconocida... (WIP)",
#             ephemeral=True
#         )

#     @discord.ui.button(label="Recolección", style=discord.ButtonStyle.primary)
#     async def recolectar(self, interaction: discord.Interaction, button: discord.ui.Button):
#         recolectar_cog = interaction.client.get_cog("RecolectarCommand")
#         if recolectar_cog is None:
#             return await interaction.response.send_message(
#                 "⚠️ Error interno: módulo de recolección no encontrado.",
#                 ephemeral=True
#             )
#         await recolectar_cog.procesar_recoleccion(interaction, self.user_id)
