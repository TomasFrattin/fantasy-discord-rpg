# bot.py (main)
# ------------------------
# IMPORTANTE:
# También creá el archivo data_loader.py en el mismo directorio con este contenido:
#
# from pathlib import Path
# import json
# p = Path(__file__).parent / "data" / "items.json"
# ITEMS = json.loads(p.read_text(encoding="utf-8"))["items_equipables"]
# ITEMS_BY_ID = { item["id"]: item for item in ITEMS }
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


# ---------- CARGA DE ITEMS / INDICES ----------
ITEMS_FILE = Path(__file__).parent / "data" / "items.json"
with open(ITEMS_FILE, "r", encoding="utf-8") as f:
    ITEMS = json.load(f)["items_equipables"]

ITEMS_BY_RARITY = {}
ITEMS_BY_ID = {}
for item in ITEMS:
    ITEMS_BY_ID[item["id"]] = item
    r = item.get("rareza", "comun")
    ITEMS_BY_RARITY.setdefault(r, []).append(item)

# (Opcional) exportar ITEMS_BY_ID a un módulo data_loader.py para que utils/db.py lo importe
# Si no querés crear data_loader.py, editá utils/db.py para importar ITEMS_BY_ID desde aquí.
# Recomiendo crear data_loader.py con el snippet indicado arriba.

RARITY_COLORS = {
    "comun": 0xB0B0B0,       # gris
    "raro": 0x3A82F7,        # azul
    "epico": 0xA335EE,       # violeta
    "legendario": 0xFF8000   # naranja
}


# ---------- BOT ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


# db.borrar_tabla_jugadores()
db.crear_tabla_jugadores()
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
