# commands/fish.py
import asyncio
import random
from datetime import datetime, timedelta
from discord import ButtonStyle, app_commands, Interaction, Embed, Color
from discord.ext import commands
from discord.ui import View, Button, button
from utils import db
from utils.messages import mensaje_usuario_no_creado, mensaje_accion_en_progreso, mensaje_funcionalidad_en_mantenimiento
import discord
from data_loader import PECES
from data.texts import mensaje_inicio_pesca
from services.jugador import obtener_jugador

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
            # Bloqueo temporal del comando
    return await interaction.response.send_message(
        embed=mensaje_funcionalidad_en_mantenimiento(),
        ephemeral=True
    )

    user_id = str(interaction.user.id)
    jugador = obtener_jugador(user_id)

    if not jugador:
        return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

    MIN_PESCA = 1
    MAX_PESCA = 60
    if minutos < MIN_PESCA or minutos > MAX_PESCA:
        return await interaction.response.send_message(
            f"❌ El tiempo de pesca debe estar entre {MIN_PESCA} y {MAX_PESCA} minutos.",
            ephemeral=True
        )

    accion = db.obtener_accion_actual(user_id)
    accion_fin_str = db.obtener_accion_fin(user_id)

    if accion and accion_fin_str:
        try:
            accion_fin = datetime.fromisoformat(accion_fin_str)
            if datetime.utcnow() >= accion_fin:
                db.actualizar_accion(user_id, None)
                db.actualizar_accion_fin(user_id, None)
                accion = None
        except Exception:
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
    accion_fin = datetime.utcnow() + timedelta(minutes=minutos)
    db.actualizar_accion(user_id, "pescando")
    db.actualizar_accion_fin(user_id, accion_fin.isoformat())

    # Embed inicial
    embed_inicio = Embed(
        title=f"¡🎣 **{jugador['username']}** ha comenzado a pescar!",
        description=mensaje_inicio_pesca(minutos),
        color=Color.blue()
    )
    view = FishView(user_id)
    await interaction.response.send_message(embed=embed_inicio, view=view, ephemeral=False)
    mensaje = await interaction.original_response()

    # Loop de actualización en tiempo real
    while True:
        if view.cancelled:
            return

        ahora = datetime.utcnow()
        if ahora >= accion_fin:
            break

        minutos_restantes = round((accion_fin - ahora).total_seconds() / 60)
        embed_inicio.set_footer(text=f"⏳ Tiempo restante aprox.: {minutos_restantes} min")

        try:
            await mensaje.edit(embed=embed_inicio, view=view)
        except Exception:
            pass  # ignorar si falla la edición

        await asyncio.sleep(10)  # chequear cada 10 segundos

    # Generar pesca
    pesca = generar_pesca(minutos)
    if pesca:
        # Agrupar duplicados
        agrupados = {}
        for p in pesca:
            if p["id"] not in agrupados:
                agrupados[p["id"]] = {"nombre": p["nombre"], "cantidad": 0, "valor": p["valor_oro"], "url": p.get("url")}
            agrupados[p["id"]]["cantidad"] += 1

        # Guardar en la base de datos usando la cantidad correcta
        for item_id, data in agrupados.items():
            db.agregar_item(user_id, item_id, data["cantidad"])

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
    else:
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
    await mensaje.edit(embed=embed_final, view=None)

class FishingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fish", description="Intentar pescar en las aguas del reino")
    @app_commands.describe(minutos="Cuánto tiempo querés pescar (en minutos)")
    async def fish(self, interaction: Interaction, minutos: int):
        await run_fish(interaction, minutos)

async def setup(bot):
    await bot.add_cog(FishingCommand(bot))
