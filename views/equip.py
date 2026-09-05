import discord
from discord.ui import View, Button
from utils import db
import logging
from services.jugadores import obtener_jugador

# Configuración básica del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        try:
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

            # Equipar item en DB
            db.equipar(self.user_id, slot, self.item["id"])

            # Obtener stats actuales del jugador
            jugador = obtener_jugador(self.user_id)

            # Preparar embed
            slot_nombre = slot.replace('_equipada', '').capitalize()
            embed = discord.Embed(title=f"⚔️ Equipaste {self.item['nombre']}", color=discord.Color.green())

            # Mostrar stats según tipo de item
            stats = self.item.get('stats', {})
            if 'vida' in stats:
                embed.add_field(name="Nueva Vida máxima", value=f"{jugador['vida_max']} HP", inline=True)

            if 'ataque' in stats:
                embed.add_field(name="Nuevo Daño", value=f"{jugador['damage']} DMG", inline=True)

            embed.set_footer(text="¡Equipado con éxito!")
            await interaction.response.edit_message(embed=embed, view=None)


        except Exception as e:
            logger.error(f"Error equipando item {self.item.get('id')} para {self.user_id}: {e}", exc_info=True)
            await interaction.response.send_message("⚠️ Ocurrió un error al equipar el ítem.", ephemeral=True)

    @discord.ui.button(label="Guardar", style=discord.ButtonStyle.secondary)
    async def guardar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"🎒 Guardaste {self.item['nombre']}",
                description="El objeto quedó disponible en tu inventario.",
                color=discord.Color.blurple(),
            ),
            view=None,
        )

    @discord.ui.button(label="Vender", style=discord.ButtonStyle.danger)
    async def vender(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        try:
            vendido, resultado = db.vender_item(self.user_id, self.item["id"])
            if not vendido:
                return await interaction.response.send_message(
                    f"❌ {resultado}.", ephemeral=True
                )

            oro = resultado["oro"]

            # Embed visual para vender
            embed = discord.Embed(title=f"💰 Vendiste {resultado['nombre']}", color=discord.Color.gold())
            embed.add_field(name="Precio", value=f"{oro} de oro", inline=False)
            embed.set_footer(text="¡Transacción completada!")

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            logger.error(f"Error vendiendo item {self.item.get('id')} para {self.user_id}: {e}", exc_info=True)
            await interaction.response.send_message("⚠️ Ocurrió un error al vender el ítem.", ephemeral=True)
