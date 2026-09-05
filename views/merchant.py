# views/merchant.py
import random
from pathlib import Path
from discord import Embed, Interaction, ButtonStyle
import discord
from discord.ui import View, Button
from utils.helpers import preparar_imagen_npc  # tu helper
from data.texts import FRASES_MERCADER

class MerchantView(View):
    def __init__(self):
        super().__init__(timeout=None)

        # Botones deshabilitados con emojis
        self.add_item(Button(
            label="Consumibles",
            style=ButtonStyle.green,
            emoji="🧪",
            custom_id="mercader_consumibles",
            disabled=True
        ))

        self.add_item(Button(
            label="Objetos",
            style=ButtonStyle.grey,
            emoji="📦",
            custom_id="mercader_objetos",
            disabled=True
        ))

    @discord.ui.button(
        label="🎣 Cañas",
        style=ButtonStyle.blurple,
        custom_id="mercader_equipo"
    )
    async def equipo(self, interaction: Interaction, button: Button):
        from views.merchant_tools import MerchantToolsView

        embed = Embed(
            title="🧰✨ Arsenal del Mercader ✨",
            description=(
                "Ah, viajero… 🧙‍♂️ aquí yace mi colección de cañas encantadas, cada una forjada con un propósito distinto:\n"
                "🎣 Algunas atraen peces del río, 🌙 otras resplandecen en lagos oscuros, y 🔮 unas pocas guardan secretos que ni la luna conoce.\n\n"
                "Sin embargo, la tradición de este mercado es clara: solo puedes llevar **una al siguiente nivel** a la vez. "
                "Elige sabiamente, y tu próxima caña te será revelada cuando domines la que tienes en mano."
            ),
            color=0x3498db
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MerchantToolsView(str(interaction.user.id)),
            attachments=[]
        )

async def mostrar_mercader(interaction: Interaction, primera_vez=True):
    frase = random.choice(FRASES_MERCADER)
    embed = Embed(
        title="🏪 El Mercader del Pueblo",
        description=frase,
        color=0xFFA500
    )

    if primera_vez:
        # Preparamos imagen solo en el primer mensaje
        ruta_imagen = Path("assets/npcs/merchant.png")
        imagen_final = preparar_imagen_npc(ruta_imagen)
        embed.set_image(url=f"attachment://{Path(imagen_final).name}")
        file = discord.File(imagen_final, filename=Path(imagen_final).name)
        try:
            await interaction.response.send_message(
                embed=embed,
                view=MerchantView(),
                file=file,
                ephemeral=True
            )
        finally:
            file.close()
            try:
                Path(imagen_final).unlink(missing_ok=True)
            except OSError:
                pass
    else:
        # Mensajes editados, sin imagen
        await interaction.response.edit_message(
            embed=embed,
            view=MerchantView()
        )
