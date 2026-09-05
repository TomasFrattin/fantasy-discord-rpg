import discord
from discord import ButtonStyle, Interaction, Embed
from discord.ui import Button, View

from utils.db import comprar_item, obtener_consumibles


class ConsumibleButton(Button):
    def __init__(self, item, owner_id):
        super().__init__(
            label=f"Comprar {item['nombre']} ({item['valor_oro']} 💰)",
            style=ButtonStyle.success,
            custom_id=f"comprar_consumible_{item['id']}",
        )
        self.item_id = item["id"]
        self.owner_id = owner_id

    async def callback(self, interaction: Interaction):
        if str(interaction.user.id) != self.owner_id:
            return await interaction.response.send_message(
                "❌ Este merchant pertenece a otro aventurero.", ephemeral=True
            )

        comprado, detalle = comprar_item(self.owner_id, self.item_id)
        if not comprado:
            return await interaction.response.send_message(
                f"❌ {detalle}.", ephemeral=True
            )

        await interaction.response.send_message(
            f"✅ Compraste **{detalle}** y se agregó a tu inventario.",
            ephemeral=True,
        )


class MerchantConsumablesView(View):
    @staticmethod
    def obtener_catalogo():
        return obtener_consumibles()

    def __init__(self, owner_id: str):
        super().__init__(timeout=60)
        self.owner_id = owner_id
        self.message = None

        for item in obtener_consumibles():
            self.add_item(ConsumibleButton(item, owner_id))

        volver = Button(
            label="Volver al mercader",
            style=ButtonStyle.secondary,
            custom_id="mercader_volver",
        )
        volver.callback = self.volver_callback
        self.add_item(volver)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    embed=discord.Embed(
                        title="⏳ Mercader cerrado",
                        description="La sección de consumibles venció. Volvé a abrir el mercader cuando quieras.",
                        color=0x808080,
                    ),
                    view=self,
                )
            except discord.HTTPException:
                pass

    async def volver_callback(self, interaction: Interaction):
        if str(interaction.user.id) != self.owner_id:
            return await interaction.response.send_message(
                "❌ Este merchant pertenece a otro aventurero.", ephemeral=True
            )

        from views.merchant import MerchantView

        self.stop()
        await interaction.response.edit_message(
            embed=Embed(
                title="🏪 El Mercader del Pueblo",
                description="El mercader vuelve a mostrar sus categorías de objetos.",
                color=0xFFA500,
            ),
            view=MerchantView(),
            attachments=[],
        )
