import discord
from discord.ext import commands
from tasks.tasks import start_all
from discord.ui import View, Button
from config import TOKEN, PREFIX, ENERGIA_MAX, WELCOME_CHANNEL_ID
from views.affinity import ElegirAfinidad
from utils import tablas
from data.texts import STARTUP_MESSAGE
from views.equip import EquiparOVender
import asyncio
from utils.locks import esta_ocupado
from utils import db

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
# tablas.borrar_tabla_jugadores()

tablas.crear_tabla_jugadores()
tablas.crear_tabla_inventario()
tablas.crear_tabla_items_consumibles()
print("Base de datos borrada y tabla recreada al iniciar el bot.")

db.resetear_todos()

async def main():
    async with bot:
        await bot.load_extension("commands.start")
        await bot.load_extension("commands.commands")  # <- tu cog de ayuda
        await bot.load_extension("commands.energy")   # <- nuevo
        await bot.load_extension("commands.profile")  # <- cog de perfil
        await bot.load_extension("commands.inventory")  # <- cog de inventario
        await bot.load_extension("commands.loot")     # <- cog de loot
        # await bot.load_extension("commands.menu") PARA UNA PROX IMPLEMENTACION, ES MAS DIFICIL VER LOS PROBLEMAS
        await bot.load_extension("commands.sleep")    # <- cog de descansar
        await bot.load_extension("commands.recolectar")
        await bot.start(TOKEN)

# -------------------- EVENTOS --------------------
@bot.event
async def on_ready():
    # Inicia todas las tasks definidas en tasks.py
    start_all(bot)

    try:
        synced = await bot.tree.sync()
        print(f"Comandos slash sincronizados: {len(synced)}")

    except Exception as e:
        print(f"Error al sincronizar comandos slash: {e}")

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(STARTUP_MESSAGE)

    print(f"Bot iniciado como {bot.user}")

# -------------------- RUN --------------------
asyncio.run(main())
