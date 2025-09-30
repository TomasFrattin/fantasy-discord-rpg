import discord
from discord.ext import commands

# Intents necesarios para que el bot lea mensajes
intents = discord.Intents.default()
intents.message_content = True

# Creamos el bot con prefijo "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para manejar energía de prueba
energia = {}

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def energia_cmd(ctx):
    """Muestra la energía actual del jugador"""
    user_id = ctx.author.id
    energia_actual = energia.get(user_id, 3)  # por defecto: 3
    await ctx.send(f"💡 {ctx.author.mention}, tenés {energia_actual} de energía.")

@bot.command()
async def loot(ctx):
    """Consume 1 energía al lootear"""
    user_id = ctx.author.id
    energia_actual = energia.get(user_id, 3)

    if energia_actual <= 0:
        await ctx.send(f"⚠️ {ctx.author.mention}, no tenés energía para lootear.")
        return

    energia[user_id] = energia_actual - 1
    await ctx.send(f"🔎 {ctx.author.mention} fue a lootear y gastó 1 energía. Te quedan {energia[user_id]}.")

# Pegá tu token entre comillas
bot.run("MTQyMjcxOTc0OTExNjEzNzYyMw.GfCA1R.LOXyUSE-4JnaVORTWcC6YOdqm2yEOZ2hWmZHrw")
