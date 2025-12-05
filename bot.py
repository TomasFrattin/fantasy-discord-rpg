# bot.py (main)
# ------------------------
# IMPORTANTE:
# También creá el archivo data_loader.py en el mismo directorio con este contenido:
#
# from pathlib import Path
# import json
# p = Path(__file__).parent / "data" / "items.json"
# ITEMS = json.loads(p.read_text(encoding="utf-8"))["items_equipables"]
# EQUIPABLES_BY_ID = { item["id"]: item for item in ITEMS }
#
# Esto lo necesita utils/db.py para recalcular stats sin import circular.
# ------------------------

import json
import random
import discord
from discord.ext import commands
from tasks.tasks import start_all
from discord.ui import View, Button
from config import TOKEN, PREFIX, ENERGIA_MAX, WELCOME_CHANNEL_ID
from views.affinity import ElegirAfinidad
from utils import db
from data.texts import STARTUP_MESSAGE
from views.equip import EquiparOVender
import datetime
from pathlib import Path
import asyncio
from discord.ext import tasks
from utils.locks import esta_ocupado
import json
from collections import defaultdict



# ---------- BOT ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.check
async def evitar_acciones_simultaneas(ctx):
    user_id = str(ctx.author.id)

    if esta_ocupado(user_id):
        await ctx.send(
            "⚠️ Ya tenés otra acción en progreso. Esperá a que termine.",
            ephemeral=True
        )
        return False

    return True

# ---------- INICIALIZACIÓN DE BASE DE DATOS ----------
# db.borrar_tabla_jugadores()

db.crear_tabla_jugadores()
db.crear_tabla_inventario()
db.crear_tabla_items_consumibles()
print("Base de datos borrada y tabla recreada al iniciar el bot.")


def obtener_tier():
    prob = random.random()
    if prob < 0.60: return "comun"
    if prob < 0.85: return "raro"
    if prob < 0.97: return "epico"
    return "legendario"


async def main():
    async with bot:
        # Cargar Cogs desde la carpeta comandos
        await bot.load_extension("commands.start")
        await bot.load_extension("commands.helpme")  # <- tu cog de ayuda
        await bot.load_extension("commands.energy")   # <- nuevo
        await bot.load_extension("commands.profile")  # <- cog de perfil
        await bot.load_extension("commands.inventory")  # <- cog de inventario
        await bot.load_extension("commands.loot")     # <- cog de loot
        # await bot.load_extension("commands.menu") PARA UNA PROX IMPLEMENTACION, ES MAS DIFICIL VER LOS PROBLEMAS
        await bot.load_extension("commands.sleep")    # <- cog de descansar
        await bot.load_extension("commands.recolectar")
        await bot.start(TOKEN)


# -------------------- COMANDOS --------------------

# -------------------- EVENTOS --------------------
@bot.event
async def on_ready():
    # Inicia todas las tasks definidas en tasks.py
    start_all(bot)

    # Sincronización de comandos slash
    try:
        # guild = discord.Object(1422721306578653186)
        # synced = await bot.tree.sync(guild=guild)
        
        synced = await bot.tree.sync()
        print(f"Comandos slash sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos slash: {e}")

    # enviar mensaje de bienvenida
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(STARTUP_MESSAGE)

    print(f"Bot iniciado como {bot.user}")
# -------------------- RUN --------------------
asyncio.run(main())
