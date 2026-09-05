# commands/menu.py
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, button, Button
from utils.messages import (
    mensaje_funcionalidad_en_progreso,
    mensaje_accion_caducada,
    mensaje_usuario_no_creado,
)

# Importar funciones independientes de otros comandos
from commands.fish import run_fish
from commands.merchant import run_merchant
from commands.craft import run_craft
from commands.sleep import run_sleep
from commands.profile import run_profile
from commands.energy import run_energy
from commands.inventory import run_inventory
from commands.forage import run_forage
from commands.hunt import run_hunt
# Para otros comandos, por ahora usamos un mensaje temporal
from discord.ui import Modal, TextInput


class FishModal(Modal):
    def __init__(self):
        super().__init__(title="🎣 Pesca")

class MenuView(View):
    """Vista principal del menú de acciones con todos los botones."""

    def __init__(self, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.message = None  # Se asignará cuando se envíe el mensaje
        
    @button(label="Hunt 🐺", style=ButtonStyle.primary)
    async def hunt_button(self, interaction: Interaction, button: Button):
        await run_hunt(interaction)

    @button(label="Forage 🧺", style=ButtonStyle.primary)
    async def forage_button(self, interaction: Interaction, button: Button):
        await run_forage(interaction)

    @button(label="Fish 🎣", style=ButtonStyle.success)
    async def fish_button(self, interaction: Interaction, button: Button):
        await run_fish(interaction)

    @button(label="Merchant 🏪", style=ButtonStyle.success)
    async def merchant_button(self, interaction: Interaction, button: Button):
        await run_merchant(interaction)

    @button(label="Craft 🔨", style=ButtonStyle.success)
    async def craft_button(self, interaction: Interaction, button: Button):
        await run_craft(interaction)

    @button(label="Inventory 🎒", style=ButtonStyle.secondary)
    async def inventory_button(self, interaction: Interaction, button: Button):
        embed = await run_inventory(interaction)
        if not embed:
            return await interaction.response.send_message(
                embed=mensaje_usuario_no_creado(),
                ephemeral=True,
            )
        from views.inventory import InventoryView
        view = InventoryView(str(interaction.user.id))
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True,
        )
        view.message = await interaction.original_response()

    @button(label="Profile 🧾", style=ButtonStyle.secondary)
    async def profile_button(self, interaction: Interaction, button: Button):
        await run_profile(interaction)

    @button(label="Energy ⚡", style=ButtonStyle.secondary)
    async def energy_button(self, interaction: Interaction, button: Button):
        await run_energy(interaction)

    @button(label="Sleep 😴", style=ButtonStyle.secondary)
    async def sleep_button(self, interaction: Interaction, button: Button):
        await run_sleep(interaction)

    async def on_timeout(self):
        """Se ejecuta cuando la vista expira."""
        if self.message:  # Solo si se envió el mensaje
            # Deshabilitar todos los botones
            for child in self.children:
                child.disabled = True

            # Editar embed mostrando mensaje de caducidad
            try:
                await self.message.edit(embed=mensaje_accion_caducada(), view=self)
            except:
                # Puede fallar si el mensaje ya desapareció o era efímero, se ignora
                pass

class MenuCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="u", description="Abrir el menú de acciones")
    async def menu(self, interaction: Interaction):
        embed = Embed(
            title="📜 Menú de Acciones",
            description=(
                "⚠️ Funcionalidad en progreso: solo para jugadores perezosos 😴\n\n"
                "Usá los botones para ejecutar acciones directamente:"
            ),
            color=0xFFD700
        )
        view = MenuView(timeout=120)
        # Guardamos el mensaje en la vista para poder editarlo luego
        message = await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()  # Referencia al mensaje enviado


async def setup(bot):
    await bot.add_cog(MenuCommand(bot))
