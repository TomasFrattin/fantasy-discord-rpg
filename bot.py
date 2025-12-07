import discord
from discord.ext import commands
from tasks.tasks import start_all
from discord.ui import View, Button
from config import TOKEN, PREFIX, WELCOME_CHANNELS
from views.affinity import ElegirAfinidad
from utils import tablas
from data.texts import STARTUP_COMMANDS
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
tablas.crear_tabla_inventario()
tablas.crear_tabla_items()
print("Base de datos borrada y tabla recreada al iniciar el bot.")

tablas.crear_tabla_jugadores()

db.resetear_todos()

# mi_id = "366690600709521419"
# db.eliminar_jugador(mi_id)
# mi_id_2 = "323250219796135937"
# db.eliminar_jugador(mi_id_2)
print("Jugador eliminado de la base de datos.")

async def main():
    async with bot:
        await bot.load_extension("commands.start")
        await bot.load_extension("commands.commands")  # <- tu cog de ayuda
        await bot.load_extension("commands.energy")   # <- nuevo
        await bot.load_extension("commands.profile")  # <- cog de perfil
        await bot.load_extension("commands.inventory")  # <- cog de inventario
        await bot.load_extension("commands.sleep")    # <- cog de descansar
        await bot.load_extension("commands.forage")
        await bot.load_extension("commands.hunt")     # <- cog de cacería
        await bot.load_extension("commands.merchant") # <- cog de mercader
        await bot.load_extension("commands.fish")     # <- cog de pesca
        await bot.load_extension("commands.menu")
        await bot.load_extension("commands.craft")    # <- cog de crafting

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

    description = "\n".join(f"- `{c['comando']}`: {c['descripcion']}" for c in STARTUP_COMMANDS)
    embed = discord.Embed(
        title="🌌 Arkanor Bot iniciado!",
        description=f"Comandos disponibles:\n\n{description}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="🧙 Que la aventura comience!")

    for channel_id in WELCOME_CHANNELS:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    print(f"Bot iniciado como {bot.user}")

# -------------------- RUN --------------------
asyncio.run(main())
