import discord
from discord.ui import View, Button
from utils import db
from data.texts import ELEMENT_DESCRIPTIONS
from utils.locks import terminar_accion

ELEMENTS = [
    {"name": "Fuego", "emoji": "🔥"},
    {"name": "Hielo", "emoji": "❄️"},
    {"name": "Tierra", "emoji": "🌍"},
    {"name": "Sombra", "emoji": "🌑"},
    {"name": "Arcano", "emoji": "🔮"},
]

class ElegirAfinidad(View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.seleccion = None

        for elem in ELEMENTS:
            btn = AfinidadButton(elem["name"], self)
            btn.emoji = elem["emoji"]
            self.add_item(btn)


class AfinidadButton(Button):
    def __init__(self, afinidad, view_obj):
        super().__init__(label=afinidad, style=discord.ButtonStyle.secondary)
        self.afinidad = afinidad
        self.view_obj = view_obj

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.view_obj.user_id:
            return await interaction.response.send_message(
                "❌ No podés elegir afinidad para otro jugador.",
                ephemeral=True
            )

        emoji = next((e["emoji"] for e in ELEMENTS if e["name"] == self.afinidad), "")
        self.view_obj.seleccion = self.afinidad

        confirm_view = ConfirmarAfinidad(self.afinidad, self.view_obj.user_id)

        await interaction.response.edit_message(
            content=f"{emoji} Elegiste **{self.afinidad}**.\n¿Confirmás tu afinidad? *No se podrá cambiar.*",
            view=confirm_view
        )


class ConfirmarAfinidad(View):
    def __init__(self, afinidad, user_id):
        super().__init__(timeout=30)
        self.afinidad = afinidad
        self.user_id = user_id

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message(
                "❌ No podés confirmar por otro jugador.",
                ephemeral=True
            )

        db.registrar_jugador(self.user_id, interaction.user.name, self.afinidad)
        description = ELEMENT_DESCRIPTIONS.get(self.afinidad, "")

        # Liberar el lock
        terminar_accion(self.user_id)

        await interaction.response.edit_message(
            content=(
                f"🧙‍♂️ **{interaction.user.name}**, tu destino está sellado.\n\n"
                f"{description}\n\n"
                "⚔️ Que tu viaje en **Arkanor** comience, y que los elementos te acompañen."
            ),
            view=None
        )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return

        # Volver a elegir, pero se mantiene la acción bloqueada (sigue en curso)
        nueva_view = ElegirAfinidad(self.user_id)

        await interaction.response.edit_message(
            content="🔁 Volvé a elegir tu afinidad:",
            view=nueva_view
        )
