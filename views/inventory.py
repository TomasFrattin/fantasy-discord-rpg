import discord
from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import Button, Select, View

from commands.inventory import construir_inventario_embed
from data_loader import EQUIPABLES_BY_ID
from services.consumibles import usar_consumible
from utils.db import obtener_inventario
from utils import db


SLOT_POR_TIPO = {
    "arma": "arma_equipada",
    "armadura": "armadura_equipada",
    "casco": "casco_equipado",
    "botas": "botas_equipadas",
}


class ConsumibleSelect(Select):
    def __init__(self, items, view):
        options = [
            SelectOption(
                label=item["nombre"],
                value=item["item_id"],
                description=f"Cantidad disponible: {item['cantidad']}",
            )
            for item in items[:25]
        ]
        super().__init__(
            placeholder="Seleccioná un consumible...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )
        self.inventory_view = view

    async def callback(self, interaction: Interaction):
        self.inventory_view.item_seleccionado = self.values[0]
        item_seleccionado = next(
            option for option in self.options if option.value == self.values[0]
        )
        for option in self.options:
            option.default = option.value == self.values[0]

        self.placeholder = f"Seleccionado: {item_seleccionado.label}"
        self.inventory_view.usar_button.disabled = False
        self.inventory_view.usar_button.label = f"Usar {item_seleccionado.label}"
        await interaction.response.edit_message(view=self.inventory_view)


class UsarConsumibleButton(Button):
    def __init__(self, owner_id):
        super().__init__(
            label="Usar seleccionado",
            style=ButtonStyle.success,
            custom_id="usar_consumible_seleccionado",
            disabled=True,
            row=2,
        )
        self.owner_id = owner_id

    async def callback(self, interaction: Interaction):
        view = self.view
        if str(interaction.user.id) != self.owner_id:
            return await interaction.response.send_message(
                "❌ Este inventario pertenece a otro aventurero.", ephemeral=True
            )

        if not view or not view.item_seleccionado:
            return await interaction.response.send_message(
                "❌ Primero seleccioná un consumible.", ephemeral=True
            )

        ok, resultado = usar_consumible(self.owner_id, view.item_seleccionado)
        if not ok:
            return await interaction.response.send_message(
                f"❌ {resultado}.", ephemeral=True
            )

        view = InventoryView(self.owner_id, "consumible")
        view.message = interaction.message
        self.view.stop()
        await interaction.response.edit_message(
            embed=construir_inventario_embed(self.owner_id, "consumible"),
            view=view,
        )
        await interaction.followup.send(
            f"✅ Usaste **{resultado['nombre']}** y recuperaste "
            f"**{resultado['recuperado']}** puntos. Quedan **{resultado['restante']}**.",
            ephemeral=True,
        )


class EquipableSelect(Select):
    def __init__(self, items, view):
        options = []
        for item in items[:25]:
            definicion = EQUIPABLES_BY_ID.get(item["item_id"], {})
            stats = definicion.get("stats", {})
            bonus = []
            if stats.get("vida"):
                bonus.append(f"+{stats['vida']} vida")
            if stats.get("ataque"):
                bonus.append(f"+{stats['ataque']} daño")
            options.append(
                SelectOption(
                    label=item["nombre"],
                    value=item["item_id"],
                    description=(f"{', '.join(bonus)} · Cantidad: {item['cantidad']}" if bonus
                                 else f"Cantidad: {item['cantidad']}"),
                )
            )

        super().__init__(
            placeholder="Seleccioná un equipable...",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
        )
        self.inventory_view = view

    async def callback(self, interaction: Interaction):
        item_id = self.values[0]
        self.inventory_view.item_seleccionado = item_id
        item = EQUIPABLES_BY_ID[item_id]
        for option in self.options:
            option.default = option.value == item_id
        self.placeholder = f"Seleccionado: {item['nombre']}"
        self.inventory_view.equipar_button.disabled = False
        self.inventory_view.equipar_button.label = f"Equipar {item['nombre']}"

        embed = construir_inventario_embed(self.inventory_view.owner_id, "equipamiento")
        jugador = self.inventory_view.obtener_jugador_actual()
        stats = item.get("stats", {})
        slot = SLOT_POR_TIPO.get(item.get("tipo"))
        actual_id = jugador[slot] if slot else None
        actual = EQUIPABLES_BY_ID.get(actual_id, {})
        actual_stats = actual.get("stats", {})
        nueva_vida_max = jugador["vida_max"] - actual_stats.get("vida", 0) + stats.get("vida", 0)
        nuevo_damage = jugador["damage"] - actual_stats.get("ataque", 0) + stats.get("ataque", 0)
        embed.add_field(
            name="🔍 Comparación",
            value=(
                f"**Actual:** {actual.get('nombre', 'Ninguno')} "
                f"(+{actual_stats.get('vida', 0)} vida, +{actual_stats.get('ataque', 0)} daño)\n"
                f"**Nuevo:** {item['nombre']} "
                f"(+{stats.get('vida', 0)} vida, +{stats.get('ataque', 0)} daño)\n\n"
                f"Vida máxima: **{jugador['vida_max']} → {nueva_vida_max}**\n"
                f"Daño: **{jugador['damage']} → {nuevo_damage}**\n"
                "La vida actual no se cura automáticamente."
            ),
            inline=False,
        )
        await interaction.response.edit_message(embed=embed, view=self.inventory_view)


class EquiparSeleccionadoButton(Button):
    def __init__(self, owner_id):
        super().__init__(
            label="Equipar seleccionado",
            style=ButtonStyle.success,
            custom_id="equipar_seleccionado",
            disabled=True,
            row=2,
        )
        self.owner_id = owner_id

    async def callback(self, interaction: Interaction):
        view = self.view
        if str(interaction.user.id) != self.owner_id:
            return await interaction.response.send_message(
                "❌ Este inventario pertenece a otro aventurero.", ephemeral=True
            )
        if not view or not view.item_seleccionado:
            return await interaction.response.send_message(
                "❌ Primero seleccioná un equipable.", ephemeral=True
            )

        ok, resultado = db.equipar_item(self.owner_id, view.item_seleccionado)
        if not ok:
            return await interaction.response.send_message(
                f"❌ {resultado}.", ephemeral=True
            )

        view = InventoryView(self.owner_id, "equipamiento")
        view.message = interaction.message
        self.view.stop()
        await interaction.response.edit_message(
            embed=construir_inventario_embed(self.owner_id, "equipamiento"),
            view=view,
        )
        await interaction.followup.send(
            f"✅ Equipaste **{resultado['nombre']}**. "
            f"Vida máxima: **{resultado['vida_max']}** · Daño: **{resultado['damage']}**.",
            ephemeral=True,
        )


class InventoryView(View):
    def __init__(self, owner_id: str, categoria="todos"):
        super().__init__(timeout=120)
        self.owner_id = owner_id
        self.message = None
        self.item_seleccionado = None
        self.usar_button = None
        self.equipar_button = None

        for label, value, style in (
            ("Todos", "todos", ButtonStyle.secondary),
            ("Consumibles", "consumible", ButtonStyle.success),
            ("Materiales", "material", ButtonStyle.primary),
            ("Equipamiento", "equipamiento", ButtonStyle.primary),
        ):
            button = Button(
                label=label,
                style=style,
                custom_id=f"inventario_{value}",
                row=0,
            )
            button.callback = self._crear_categoria_callback(value)
            self.add_item(button)

        if categoria == "consumible":
            consumibles = [
                item
                for item in obtener_inventario(owner_id)
                if item["tipo"] == "consumible" and item["cantidad"] > 0
            ]
            if consumibles:
                self.add_item(ConsumibleSelect(consumibles, self))
                self.usar_button = UsarConsumibleButton(owner_id)
                self.add_item(self.usar_button)

        if categoria == "equipamiento":
            equipables = [
                item for item in obtener_inventario(owner_id)
                if item["tipo"] in SLOT_POR_TIPO and item["cantidad"] > 0
            ]
            if equipables:
                self.add_item(EquipableSelect(equipables, self))
                self.equipar_button = EquiparSeleccionadoButton(owner_id)
                self.add_item(self.equipar_button)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        if not self.message:
            return

        try:
            await self.message.edit(
                embed=discord.Embed(
                    title="⏳ Inventario vencido",
                    description="Este menú expiró. Usá `/inventory` para abrirlo de nuevo.",
                    color=0x808080,
                ),
                view=self,
            )
        except discord.HTTPException:
            pass

    def obtener_jugador_actual(self):
        from services.jugadores import obtener_jugador
        return obtener_jugador(self.owner_id)

    def _crear_categoria_callback(self, categoria):
        async def callback(interaction: Interaction):
            if str(interaction.user.id) != self.owner_id:
                return await interaction.response.send_message(
                    "❌ Este inventario pertenece a otro aventurero.", ephemeral=True
                )

            view = InventoryView(self.owner_id, categoria)
            view.message = interaction.message
            self.stop()
            await interaction.response.edit_message(
                embed=construir_inventario_embed(self.owner_id, categoria),
                view=view,
            )

        return callback
