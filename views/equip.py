import discord
from discord.ui import View, Button
from utils import db

class EquiparOVender(View):
    """
    View genérica: recibe el item encontrado. Decide equipar -> llama db.equipar(slot, item_id)
    o vender -> db.sumar_oro(...)
    """
    def __init__(self, user_id, item, slot_col=None):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.item = item
        self.slot_col = slot_col

    @discord.ui.button(label="Equipar", style=discord.ButtonStyle.success)
    async def equipar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        tipo = self.item.get("tipo")
        slot_map = {
            "arma": "arma_equipada",
            "armadura": "armadura_equipada",
            "casco": "casco_equipado",
            "botas": "botas_equipadas"
        }
        slot = self.slot_col or slot_map.get(tipo)
        if not slot:
            return await interaction.response.send_message("Tipo de ítem no reconocible.", ephemeral=True)

        db.equipar(self.user_id, slot, self.item["id"])
        await interaction.response.edit_message(content=f"⚔️ Equipaste **{self.item['nombre']}**.", view=None)

    @discord.ui.button(label="Vender", style=discord.ButtonStyle.danger)
    async def vender(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return
        oro = self.item.get("valor_oro", 0)
        db.sumar_oro(self.user_id, oro)
        await interaction.response.edit_message(content=f"💰 Vendiste **{self.item['nombre']}** por **{oro}** de oro.", view=None)
