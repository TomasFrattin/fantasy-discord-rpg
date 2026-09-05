# views/merchant_tools.py
import discord
from discord.ui import View, Button
from discord import ButtonStyle, Interaction, Embed
from utils.helpers import canas_ordenadas
from services.jugadores import obtener_jugador, sumar_oro
from utils.db import equipar
from data.canas import CANAS



def puede_comprar(user_id, precio):
    jugador = obtener_jugador(user_id)
    if not jugador:
        return False
    return jugador["oro"] >= precio


class CanaButton(Button):
    def __init__(self, cana_id, cana_data, habilitada, label=None):
        super().__init__(
            label=label if label else f"{cana_data['nombre']} (Tier {cana_data['tier']})",
            style=ButtonStyle.green if habilitada else ButtonStyle.grey,
            disabled=not habilitada,
            custom_id=f"buy_{cana_id}"
        )
        self.cana_id = cana_id
        self.cana_data = cana_data
        self.callback = self.comprar_cana  # <--- registrar el callback

    async def comprar_cana(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        if not puede_comprar(user_id, self.cana_data["precio"]):
            embed = discord.Embed(
                title="❌ No tenés suficiente oro",
                description=f"La **{self.cana_data['nombre']}** cuesta {self.cana_data['precio']} de oro.",
                color=0xe74c3c
            )
            return await interaction.response.edit_message(embed=embed, attachments=[])

        # Descontamos oro y equipamos
        sumar_oro(user_id, -self.cana_data["precio"])
        equipar(user_id, "cana_equipada", self.cana_id)

        embed = discord.Embed(
            title=f"🛒 Has adquirido la **{self.cana_data['nombre']}** 🎣",
            description=(
                f"{self.cana_data['descripcion']}\n\n"
                f"💰 Gastaste **{self.cana_data['precio']}** de oro"
            ),
            color=0x2ecc71
        )

        await interaction.response.edit_message(embed=embed, view=None, attachments=[])


class MerchantToolsView(View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    embed=Embed(
                        title="⏳ Mercader cerrado",
                        description="La sección de cañas venció. Volvé a abrir el mercader cuando quieras.",
                        color=0x808080,
                    ),
                    view=self,
                )
            except discord.HTTPException:
                pass

    def __init__(self, user_id: str):
        super().__init__(timeout=60)
        self.message = None

        jugador = obtener_jugador(user_id)
        cana_actual = jugador["cana_equipada"]

        canas = canas_ordenadas()

        # Detectamos cuál es la siguiente comprable
        siguiente_cana_id = None
        if cana_actual:
            for idx, (cid, _) in enumerate(canas):
                if cid == cana_actual and idx + 1 < len(canas):
                    siguiente_cana_id = canas[idx + 1][0]
        else:
            siguiente_cana_id = canas[0][0]

        for cana_id, data in canas:
            habilitada = cana_id == siguiente_cana_id
            self.add_item(CanaButton(
                cana_id,
                data,
                habilitada,
                label=f"{data['nombre']} ({data['precio']} 💰)"
            ))
