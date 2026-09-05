import discord
from discord import ButtonStyle, Embed, Interaction, SelectOption
from discord.ui import Button, Select, View

from utils.db import obtener_objetos_vendibles, vender_item


class ObjetosVendiblesSelect(Select):
    def __init__(self, objetos, view):
        options = [
            SelectOption(
                label=objeto["nombre"],
                value=objeto["item_id"],
                description=(
                    f"{objeto['valor_oro']} 💰 · Cantidad: {objeto['cantidad']}"
                    + (" · Equipado" if objeto["equipado"] else "")
                ),
            )
            for objeto in objetos[:25]
        ]
        super().__init__(
            placeholder="Seleccioná un objeto para vender...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )
        self.sell_view = view

    async def callback(self, interaction: Interaction):
        self.sell_view.item_seleccionado = self.values[0]
        seleccionado = next(option for option in self.options if option.value == self.values[0])
        for option in self.options:
            option.default = option.value == self.values[0]
        self.placeholder = f"Seleccionado: {seleccionado.label}"
        self.sell_view.vender_button.disabled = False
        self.sell_view.vender_button.label = f"Vender {seleccionado.label}"
        await interaction.response.edit_message(view=self.sell_view)


class VenderSeleccionadoButton(Button):
    def __init__(self, owner_id):
        super().__init__(
            label="Vender seleccionado",
            style=ButtonStyle.danger,
            custom_id="vender_objeto_seleccionado",
            disabled=True,
            row=2,
        )
        self.owner_id = owner_id

    async def callback(self, interaction: Interaction):
        view = self.view
        if str(interaction.user.id) != self.owner_id:
            return await interaction.response.send_message(
                "❌ Este merchant pertenece a otro aventurero.", ephemeral=True
            )
        if not view or not view.item_seleccionado:
            return await interaction.response.send_message(
                "❌ Primero seleccioná un objeto.", ephemeral=True
            )

        vendido, resultado = vender_item(self.owner_id, view.item_seleccionado)
        if not vendido:
            return await interaction.response.send_message(
                f"❌ {resultado}.", ephemeral=True
            )

        nueva_view = MerchantSellView(self.owner_id)
        nueva_view.message = interaction.message
        await interaction.response.edit_message(
            embed=Embed(
                title="💰 Objeto vendido",
                description=(
                    f"Vendiste **{resultado['nombre']}** por **{resultado['oro']} de oro**.\n\n"
                    "Podés seleccionar otro objeto para vender."
                ),
                color=0x2ECC71,
            ),
            view=nueva_view,
        )


class MerchantSellView(View):
    def __init__(self, owner_id: str):
        super().__init__(timeout=60)
        self.owner_id = owner_id
        self.message = None
        self.item_seleccionado = None
        self.vender_button = None

        objetos = obtener_objetos_vendibles(owner_id)
        if objetos:
            self.add_item(ObjetosVendiblesSelect(objetos, self))
            self.vender_button = VenderSeleccionadoButton(owner_id)
            self.add_item(self.vender_button)
        else:
            self.add_item(Button(
                label="No tenés equipables para vender",
                style=ButtonStyle.secondary,
                disabled=True,
                row=1,
            ))

        volver = Button(
            label="Volver al mercader",
            style=ButtonStyle.secondary,
            custom_id="mercader_volver_desde_venta",
            row=0,
        )
        volver.callback = self.volver_callback
        self.add_item(volver)

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

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    embed=Embed(
                        title="⏳ Mercader cerrado",
                        description="La sección de venta venció. Volvé a abrir el merchant cuando quieras.",
                        color=0x808080,
                    ),
                    view=self,
                )
            except discord.HTTPException:
                pass
