# commands/fish.py
import asyncio
import random
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from utils.messages import mensaje_usuario_no_creado

# Lista de peces y sus probabilidades (peso)
PECES = [
    {"id": "pez_comun", "nombre": "Pez Común", "rareza": "comun", "peso": 50, "valor": 5},
    {"id": "pez_raro", "nombre": "Pez Raro", "rareza": "raro", "peso": 20, "valor": 15},
    {"id": "pez_epico", "nombre": "Pez Épico", "rareza": "epico", "peso": 5, "valor": 50},
]

# Diccionario para controlar tareas de pesca activas por usuario
active_fishing_tasks = {}

async def run_fish(interaction: Interaction, minutos: int):
    user_id = str(interaction.user.id)
    jugador = db.obtener_jugador(user_id)
    if not jugador:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)
    
    # Verificar si ya está pescando
    if user_id in active_fishing_tasks:
        embed = Embed(
            title="⚠️ Ya estás pescando",
            description="No podés iniciar otra acción hasta terminar o cancelar la actual.",
            color=0xF2A93B
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Marcar jugador como pescando en DB
    db.actualizar_accion(user_id, "pescando")

    embed_inicio = Embed(
        title="🎣 Comenzaste a pescar",
        description=f"Vas a pescar durante {minutos} minutos. ¡Suerte!",
        color=0x3BA3F2
    )
    await interaction.response.send_message(embed=embed_inicio, ephemeral=True)

    # Lista donde acumularemos lo pescado
    pesca = []

    async def fishing_task():
        ticks = minutos  # 1 tick por minuto
        for _ in range(ticks):
            await asyncio.sleep(60)  # esperar 1 minuto
            # Selección ponderada de peces según peso
            pez = random.choices(PECES, weights=[p['peso'] for p in PECES], k=1)[0]
            pesca.append(pez)
            db.agregar_item(user_id, pez['id'], 1)
        # Al finalizar
        db.actualizar_accion(user_id, None)
        # Crear resumen
        resumen = "\n".join(f"{p['nombre']} (valor {p['valor']})" for p in pesca)
        embed_final = Embed(
            title="🏆 Pesca terminada",
            description=f"Esto fue lo que pescaste:\n{resumen}",
            color=0x3BA3F2
        )
        await interaction.followup.send(embed=embed_final)
        # Quitar de tareas activas
        active_fishing_tasks.pop(user_id, None)

    # Guardar la tarea y ejecutarla
    task = asyncio.create_task(fishing_task())
    active_fishing_tasks[user_id] = task

# Comando
class FishingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fish", description="Intentar pescar en las aguas del reino")
    @app_commands.describe(minutos="Cuánto tiempo querés pescar (en minutos)")
    async def fish(self, interaction: Interaction, minutos: int):
        await run_fish(interaction, minutos)

    @app_commands.command(name="cancel_fish", description="Cancelar tu pesca actual")
    async def cancel_fish(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        task = active_fishing_tasks.get(user_id)
        if task:
            task.cancel()
            db.actualizar_accion(user_id, None)
            active_fishing_tasks.pop(user_id, None)
            embed = Embed(
                title="❌ Pesca cancelada",
                description="Recibiste lo que habías pescado hasta ahora.",
                color=0xF23B3B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("No estás pescando actualmente.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FishingCommand(bot))
