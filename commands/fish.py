# commands/fish.py
import random
import time
import discord
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
import os
import asyncio
from utils.messages import mensaje_usuario_no_creado
from data_loader import PECES
from data.texts import ENCUENTRO_VIEJO_PESCADOR
from services.jugadores import obtener_jugador, sumar_oro
from services.acciones import actualizar_accion, actualizar_accion_fin
from views.fish import PrimeraCanaView
from utils.helpers import preparar_imagen_pez
from data.canas import CANAS
from config import configurar_logging
import logging 
from views.combat import CombatView
from utils.combat_manager import create_combat

configurar_logging()

COOLDOWN_PESCA = 1020  # segundos
minutos_cooldown = COOLDOWN_PESCA // 60
segundos_cooldown = COOLDOWN_PESCA % 60

def elegir_pez_por_peso(peces):
    pesos = [p["peso"] for p in peces]
    return random.choices(peces, weights=pesos, k=1)[0]


def peces_por_cana(cana_id: str):
    cana = CANAS.get(cana_id)
    if not cana:
        return []

    rarezas_permitidas = cana["rareza_permitida"]
    return [p for p in PECES if p["rareza"] in rarezas_permitidas]


async def run_fish(interaction: Interaction):

    user_id = str(interaction.user.id)
    jugador = obtener_jugador(user_id)

    if not jugador:
        return await interaction.response.send_message(
            embed=mensaje_usuario_no_creado(),
            ephemeral=True
        )

    # ─────────────────────────────
    # PRIMERA VEZ SIN CAÑA
    # ─────────────────────────────
    if not jugador["cana_equipada"]:
        embed = Embed(
            title=ENCUENTRO_VIEJO_PESCADOR["titulo"],
            description=ENCUENTRO_VIEJO_PESCADOR["descripcion"],
            color=Color.gold()
        )
        view = PrimeraCanaView(user_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        try:
            await asyncio.wait_for(view.wait(), timeout=120.0)
        except asyncio.TimeoutError:
            # El usuario no interactuó dentro del timeout
            logging.warning(f"[FISH] Usuario {user_id} ({jugador['username']}) no interactuó con la vista de caña (timeout).")
        return

    now = int(time.time())

    # ─────────────────────────────
    # COOLDOWN
    # ─────────────────────────────
    if jugador["accion_fin"] and jugador["accion_fin"] > now:
        restante = jugador["accion_fin"] - now
        minutos_restantes = restante // 60
        segundos_restantes = restante % 60
        embed = discord.Embed(
            title="⏳ Enfriamiento de pesca",
            description=f"Todavía estás esperando que piquen…\n**{minutos_restantes} min {segundos_restantes} s** restantes",
            color=discord.Color.orange()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        actualizar_accion_fin(user_id, None)

    # ─────────────────────────────
    # PESCA
    # ─────────────────────────────
    peces_disponibles = peces_por_cana(jugador["cana_equipada"])

    if not peces_disponibles:
        return await interaction.response.send_message(
            "🎣 No hay peces disponibles para esta caña.",
            ephemeral=True
        )

    pez = elegir_pez_por_peso(peces_disponibles)
    cana = CANAS[jugador["cana_equipada"]]

    if pez.get("hostil", False):
        actualizar_accion_fin(user_id, now + COOLDOWN_PESCA)

        combat_payload = {
            "mob_id": pez["id"],
            "mob_nombre": pez["nombre"],
            "mob_emoji": "🐟",
            "mob_hp": pez["vida_max"],
            "mob_hp_max": pez["vida_max"],
            "mob_valor_oro": pez["valor_oro"],
            "mob_atk": pez["ataque"],
            "mob_exp": pez["exp"],
            "mob_loot_bonus": 0,
            "player_hp": jugador["vida"],
            "player_hp_max": jugador["vida_max"],
            "image_shown": False,
        }
        create_combat(user_id, combat_payload)
        

        embed = Embed(
            title="⚔️ ¡Has pescado un pez hostil!",
            description=(
                f"🎯 **Caña usada:** {cana['nombre']}\n\n"
                f"🐟 **{pez['nombre']}**\n"
                f"_{pez['descripcion']}_\n\n"
                f"⏳ Prepárate para luchar contra él."
            ),
            color=0xFF4500
        )
        view = CombatView(user_id)
        
        pez_img_path = preparar_imagen_pez(f"assets/peces/{os.path.basename(pez['url'])}", size=(280,280))
        if pez_img_path and pez_img_path.exists():
            file = discord.File(pez_img_path, filename=pez_img_path.name)
            embed.set_image(url=f"attachment://{pez_img_path.name}")
            await interaction.response.send_message(embed=embed, view=view, file=file)
            try: os.remove(pez_img_path)
            except: pass
        else:
            await interaction.response.send_message(embed=embed, view=view)

        return

    oro_ganado = pez["valor_oro"]

    sumar_oro(user_id, oro_ganado)

    # actualizar_accion(user_id, "pescar")
    actualizar_accion_fin(user_id, now + COOLDOWN_PESCA)

    embed = Embed(
        title="🎣 ¡Pescaste algo!",
        description=(
            f"🎯 **Caña usada:** {cana['nombre']}\n\n"
            f"🐟 **{pez['nombre']}**\n"
            f"_{pez['descripcion']}_\n\n"
            f"💰 Ganaste **{oro_ganado} de oro**\n"
            f"⏳ Podés volver a pescar en **{minutos_cooldown} min {segundos_cooldown} s**"
        ),
        color=Color.blue()
    )

    logging.info(
        f"[FISH] Usuario {user_id} ({jugador['username']}) "
        f"usó {cana['nombre']} y pescó {pez['nombre']} "
        f"({pez['rareza']}) por {oro_ganado} oro."
    )
    pez_img_path = preparar_imagen_pez(f"assets/peces/{os.path.basename(pez['url'])}", size=(280,280))
    if pez_img_path and pez_img_path.exists():
        file = discord.File(pez_img_path, filename=pez_img_path.name)
        embed.set_image(url=f"attachment://{pez_img_path.name}")
        await interaction.response.send_message(embed=embed, file=file)
        try: os.remove(pez_img_path)
        except: pass
    else:
        await interaction.response.send_message(embed=embed)

class FishingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="fish",
        description="Intentar pescar en las aguas del reino"
    )
    async def fish(self, interaction: Interaction):
        await run_fish(interaction)


async def setup(bot):
    await bot.add_cog(FishingCommand(bot))
