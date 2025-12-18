import random
import discord
from services.jugadores import sumar_oro
from utils.db import equipar
from data_loader import EQUIPABLES_BY_RARITY

RECOMPENSAS = {
    1: {"oro": 400, "rareza": "legendario", "slot": "arma_equipada"},
    2: {"oro": 300, "rareza": "epico", "slot": "arma_equipada"},
    3: {"oro": 200, "rareza": "raro", "slot": "arma_equipada"},
}

TIPO_A_SLOT = {
    "arma": "arma_equipada",
    "armadura": "armadura_equipada",
    "casco": "casco_equipado",
    "botas": "botas_equipadas",
    "cana": "cana_equipada"
}

async def recompensar_top(interaction: discord.Interaction, top_ranking):
    """Da las recompensas automáticamente y muestra un embed del podio."""

    # Embed principal con mensaje general
    embed = discord.Embed(
        title="🏆 ¡Recompensas del Evento!",
        description=(
            "✨ Los héroes que más contribuyeron han sido honrados con sus **botines legendarios**. "
            "Que sus nombres resuenen en la historia del reino ⚔️💰"
        ),
        color=discord.Color.gold()
    )

    for i, jugador in enumerate(top_ranking, start=1):
        recompensa = RECOMPENSAS[i]
        equipables = EQUIPABLES_BY_RARITY.get(recompensa["rareza"], [])
        if not equipables:
            print(f"[WARN] No hay equipables para la rareza '{recompensa['rareza']}'")
            continue  # Evita romper el bot si no hay items

        item = random.choice(equipables)

        # Determinar slot real según tipo de item
        slot_real = TIPO_A_SLOT.get(item["tipo"], "arma_equipada")  # fallback por si no coincide
        
        # Dar oro y equipar automáticamente
        sumar_oro(jugador["user_id"], recompensa["oro"])
        equipar(jugador["user_id"], slot_real, item["id"])

        # Medalla según posición
        medalla = ["🥇","🥈","🥉"][i-1]

        # Field individual para cada jugador (texto breve, no repetitivo)
        embed.add_field(
            name=f"{medalla} {jugador['username']}",
            value=f"💰 {recompensa['oro']} de oro y **{item['nombre']}** ({item['rareza']}) ⚔️",
            inline=False
        )

    # Enviar el embed completo
    await interaction.followup.send(embed=embed)
