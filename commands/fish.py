# commands/fish.py
import asyncio
import random
from datetime import datetime, timedelta
from discord import ButtonStyle, app_commands, Interaction, Embed, Color
from discord.ext import commands
from discord.ui import View, Button, button
from utils import db
from utils.messages import mensaje_usuario_no_creado, mensaje_accion_en_progreso
import discord
from data_loader import PECES
from data.texts import mensaje_inicio_pesca

class FishView(View):
    def __init__(self, user_id: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.cancelled = False

    @discord.ui.button(label="Cancelar pesca", style=ButtonStyle.danger)
    async def cancelar(self, interaction: Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("Este botón no es para vos.", ephemeral=True)
        
        self.cancelled = True
        db.actualizar_accion(self.user_id, None)
        db.actualizar_accion_fin(self.user_id, None)

        embed = Embed(
            title="❌ Pesca cancelada",
            description="La pesca fue cancelada.",
            color=Color.red()
        )
        self.stop()
        await interaction.response.edit_message(embed=embed, view=None)

def generar_pesca(minutos: int):
    """Genera los peces según la duración de la pesca, incluyendo posibilidad de no sacar nada."""
    pesca = []
    for _ in range(minutos):
        # Chance de que no salga nada (por ejemplo 60%)
        if random.random() < 0.6:
            continue  # No se captura nada este minuto

        pez = random.choices(PECES, weights=[p["peso"] for p in PECES], k=1)[0]
        pesca.append(pez)
    return pesca

async def run_fish(interaction: Interaction, minutos: int):
    user_id = str(interaction.user.id)
    jugador = db.obtener_jugador(user_id)
    if not jugador:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

    accion = db.obtener_accion_actual(user_id)
    accion_fin_str = db.obtener_accion_fin(user_id)

    if accion and accion_fin_str:
        try:
            accion_fin = datetime.fromisoformat(accion_fin_str)
            if datetime.utcnow() >= accion_fin:
                # La acción ya expiró, limpiamos
                db.actualizar_accion(user_id, None)
                db.actualizar_accion_fin(user_id, None)
                accion = None  # Continuamos con la pesca
        except Exception:
            # Si el formato de la fecha es inválido, limpiamos
            db.actualizar_accion(user_id, None)
            db.actualizar_accion_fin(user_id, None)
            accion = None

    accion = db.obtener_accion_actual(user_id)
    if accion:
        return await interaction.response.send_message(
            embed=mensaje_accion_en_progreso(user_id),
            ephemeral=True
        )

    # Registrar acción
    accion_fin = datetime.now() + timedelta(minutes=minutos)
    db.actualizar_accion(user_id, "pescando")
    db.actualizar_accion_fin(user_id, accion_fin.isoformat())

    # Embed de inicio
    embed_inicio = Embed(
        title=f"¡🎣 **{jugador['username']}** ha comenzado a pescar!",
        description=mensaje_inicio_pesca(minutos),  # <-- acá sí pasás el valor real
        color=Color.blue()
    )
    view = FishView(user_id)
    await interaction.response.send_message(embed=embed_inicio, view=view, ephemeral=False)

    mensaje = await interaction.original_response()

    tiempo_restante = minutos * 60  # segundos
    intervalo_update = 2 * 60       # 2 minutos

    while tiempo_restante > 0:
        sleep_time = min(intervalo_update, tiempo_restante)
        await asyncio.sleep(sleep_time)
        tiempo_restante -= sleep_time

        if view.cancelled:
            return

        minutos_restantes = max(0, round(tiempo_restante / 60))
        embed_inicio.set_footer(text=f"⏳ Tiempo restante aprox.: {minutos_restantes} min")
        await mensaje.edit(embed=embed_inicio, view=view)

    # Generar pesca
    pesca = generar_pesca(minutos)
    if pesca:
        for pez in pesca:
            db.agregar_item(user_id, pez["id"], 1)

        # Agrupar duplicados
        agrupados = {}
        for p in pesca:
            if p["id"] not in agrupados:
                agrupados[p["id"]] = {"nombre": p["nombre"], "cantidad": 0, "valor": p["valor_oro"], "url": p.get("url")}
            agrupados[p["id"]]["cantidad"] += 1

        texto_flavor = random.choice([
            "¡Qué buena pesca! Parece que la fortuna está de tu lado. 🐟",
            "Los peces han caído en tu red. ¡Un día productivo! 🎣",
            "¡Hora de contar los tesoros del agua! 🌊",
            "Tu paciencia ha dado frutos, algunos peces se unen a tu inventario. 🐠",
        ])

        embed_final = Embed(
            title="🏆 Pesca terminada",
            description=texto_flavor,
            color=Color.green()
        )

        for info in agrupados.values():
            embed_final.add_field(
                name=info["nombre"],
                value=f"Cantidad: × {info['cantidad']}\n",
                inline=True
            )

        # Placeholder para collage futuro
        rutas_imagenes = [p.get("url") for p in agrupados.values() if p.get("url")]
        # Aquí podrías generar el collage como en forage

    else:
        # No se pescó nada
        embed_final = Embed(
            title="😢 Pesca vacía",
            description=random.choice([
                "Intentaste pescar, pero los peces no estaban de humor hoy. 🍂",
                "Las aguas están tranquilas, pero tu caña no atrapó nada. 🌊",
                "Hoy los peces han sido esquivos. ¡No pierdas la esperanza! 🐟",
                "Nada muerde tu anzuelo... mejor suerte la próxima vez. 🎣",
            ]),
            color=Color.orange()
        )

    # Fin de la pesca
    db.actualizar_accion(user_id, None)
    db.actualizar_accion_fin(user_id, None)
    await interaction.edit_original_response(embed=embed_final, view=None)

class FishingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fish", description="Intentar pescar en las aguas del reino")
    @app_commands.describe(minutos="Cuánto tiempo querés pescar (en minutos)")
    async def fish(self, interaction: Interaction, minutos: int):
        await run_fish(interaction, minutos)

async def setup(bot):
    await bot.add_cog(FishingCommand(bot))
