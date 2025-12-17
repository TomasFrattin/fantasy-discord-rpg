import random
import discord
from services.jugadores import sumar_oro, equipar
from data_loader import EQUIPABLES_BY_RARITY

RECOMPENSAS = {
    1: {"oro": 500, "rareza": "rara", "slot": "arma_equipada"},
    2: {"oro": 300, "rareza": "epica", "slot": "arma_equipada"},
    3: {"oro": 200, "rareza": "rara", "slot": "arma_equipada"},
}

async def recompensar_top(interaction: discord.Interaction, top_ranking):
    """Da las recompensas automáticamente y muestra un embed del podio."""
    embed = discord.Embed(
        title="🎉 ¡El fondo fue completado! Recompensas del ranking",
        color=discord.Color.gold()
    )

    for i, jugador in enumerate(top_ranking, start=1):
        recompensa = RECOMPENSAS[i]
        # Elegir item aleatorio de la rareza
        item = random.choice(EQUIPABLES_BY_RARITY[recompensa["rareza"]])
        # Dar oro y equipar automáticamente
        sumar_oro(jugador["user_id"], recompensa["oro"])
        equipar(jugador["user_id"], recompensa["slot"], item["id"])
        # Agregar al embed
        medalla = ["🥇","🥈","🥉"][i-1]
        embed.add_field(
            name=f"{medalla} {jugador['username']}",
            value=f"Recibió {recompensa['oro']} de oro y el arma **{item['nombre']}** ({item['rareza']})",
            inline=False
        )

    await interaction.followup.send(embed=embed)
