# commands/menu.py
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, button, Button
from utils.messages import mensaje_funcionalidad_en_progreso, mensaje_accion_caducada

# Importar funciones independientes de otros comandos
from commands.fish import run_fish
from commands.merchant import run_merchant
from commands.craft import run_craft
from commands.sleep import run_sleep
from commands.profile import run_profile
from commands.energy import run_energy
# Para otros comandos, por ahora usamos un mensaje temporal
from discord.ui import Modal, TextInput

MIN_PESCA = 1
MAX_PESCA = 60

class FishModal(Modal):
    def __init__(self):
        super().__init__(title="🎣 Pesca")
        self.minutos_input = TextInput(
            label=f"Minutos a pescar ({MIN_PESCA}-{MAX_PESCA})",
            placeholder="Ej: 10",
            required=True,
            max_length=3  # suficiente para 120 minutos
        )
        self.add_item(self.minutos_input)

    async def on_submit(self, interaction: Interaction):
        try:
            minutos = int(self.minutos_input.value)
            if minutos < MIN_PESCA or minutos > MAX_PESCA:
                await interaction.response.send_message(
                    f"❌ Debés ingresar un número entre {MIN_PESCA} y {MAX_PESCA}.",
                    ephemeral=True
                )
                return

            # Llamada a tu función principal de pesca
            await run_fish(interaction, minutos)

        except ValueError:
            await interaction.response.send_message(
                "❌ Debés ingresar un número válido.",
                ephemeral=True
            )
class MenuView(View):
    """Vista principal del menú de acciones con todos los botones."""

    def __init__(self, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.message = None  # Se asignará cuando se envíe el mensaje
        
    @button(label="Hunt 🐺", style=ButtonStyle.primary)
    async def hunt_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_message(embed=mensaje_funcionalidad_en_progreso(), ephemeral=True)

    @button(label="Forage 🧺", style=ButtonStyle.primary)
    async def forage_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_message(embed=mensaje_funcionalidad_en_progreso(), ephemeral=True)

    @button(label="Fish 🎣", style=ButtonStyle.success)
    async def fish_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(FishModal())

    @button(label="Merchant 🏪", style=ButtonStyle.success)
    async def merchant_button(self, interaction: Interaction, button: Button):
        await run_merchant(interaction)

    @button(label="Craft 🔨", style=ButtonStyle.success)
    async def craft_button(self, interaction: Interaction, button: Button):
        await run_craft(interaction)

    @button(label="Inventory 🎒", style=ButtonStyle.secondary)
    async def inventory_button(self, interaction: Interaction, button: Button):
        await interaction.response.send_message(embed=mensaje_funcionalidad_en_progreso(), ephemeral=True)

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
