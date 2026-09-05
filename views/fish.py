import discord
from discord.ui import View, Button
from discord import Embed, Color, ButtonStyle
import random
from utils import db
from services.jugadores import obtener_jugador, actualizar_cana, sumar_oro
from services.acciones import actualizar_accion, actualizar_accion_fin

class PrimeraCanaView(View):
    def __init__(self, user_id: str):
        super().__init__(timeout=120)  # 2 minutos de timeout
        self.user_id = user_id
        self.interacted = False
        self.message = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    embed=Embed(
                        title="⏳ Decisión vencida",
                        description="No elegiste una caña a tiempo. Podés volver a usar `/fish` cuando quieras.",
                        color=Color.grey(),
                    ),
                    view=self,
                )
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Aceptar la caña rústica", style=ButtonStyle.success)
    async def aceptar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message(
                "❌ Este botón no es para vos.",
                ephemeral=True
            )

        self.interacted = True
        actualizar_cana(self.user_id, "cana_rustica")
        embed = Embed(
            title="🎣 ¡Recibiste tu primera caña!",
            description=(
                "El viejo pescador asiente en silencio y te entrega la caña con manos temblorosas 🎣.\n"
                "Sin decir una palabra más, se aleja lentamente del muelle, perdiéndose entre el sonido del viento y las olas 🌊.\n\n"
                "Ahora, con la caña en tus manos, estás listo para comenzar tu propia jornada de pesca.", 
            ),
            color=Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="Darle algo de oro (10)", style=ButtonStyle.primary)
    async def pagar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message(
                "❌ Este botón no es para vos.",
                ephemeral=True
            )

        self.interacted = True
        jugador = obtener_jugador(self.user_id)
        costo = 10
        if jugador["oro"] >= costo:
            sumar_oro(self.user_id, jugador["oro"] - costo)
            actualizar_cana(self.user_id, "cana_rustica")
            embed = Embed(
                title="💰 Pagaste la caña",
                description=(
                    f"Contás unas monedas y se las entregás al anciano 💰.\n"
                    f"Con una leve sonrisa, acepta el pago y te entrega la caña rústica 🎣.\n\n"
                    f"Pagaste {costo} de oro y ahora nada te impide lanzar el anzuelo al agua."
                ),
                color=Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
        else:
            await interaction.response.send_message(
                "❌ No tenés suficiente oro.",
                ephemeral=True
            )

    @discord.ui.button(label="No la quiero", style=ButtonStyle.danger)
    async def irme(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return
        self.interacted = True
        embed = Embed(
            title="🚶 Te retiras",
            description=(
                "Negás con la cabeza y das un paso atrás 🚶.\n"
                "El anciano no parece sorprendido; simplemente asiente y vuelve su mirada al mar 🌊.\n\n"
                "Te alejás del muelle mientras el sonido del agua golpeando la madera queda atrás."
            ),          
            color=Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

