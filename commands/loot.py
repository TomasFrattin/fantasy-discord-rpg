# commands/loot.py
import random
from typing import Counter
import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from data_loader import EQUIPABLES, EQUIPABLES_BY_ID
from views.equip import EquiparOVender
from services.jugador import obtener_energia, gastar_energia

RARITY_COLORS = {
    "comun": 0xB0B0B0,
    "poco_comun": 0x4CAF50,
    "raro": 0x3A82F7,
    "epico": 0xA335EE,
    "legendario": 0xFF8000
}

RARITY_EMOJIS = {
    "comun": "🔹",
    "poco_comun": "🟢",
    "raro": "🔷",
    "epico": "💜",
    "legendario": "🔥"
}

EQUIPABLES_BY_RARITY = {}
for item in EQUIPABLES:
    r = item.get("rareza", "comun")
    EQUIPABLES_BY_RARITY.setdefault(r, []).append(item)


def obtener_tier(nivel_hunt):
    """
    Devuelve la rareza de un ítem según el nivel de hunt del jugador.
    Nunca permite legendarios o épicos si el nivel no está desbloqueado.
    """
    prob = random.random()  # 0.0 - 1.0

    # Probabilidades base
    base_probs = {
        "comun": 0.60,
        "poco_comun": 0.25,  # probabilidad incremental
        "raro": 0.04,
        "epico": 0.01,     
        "legendario": 0.005
    }

    # Ajustar según nivel
    if nivel_hunt < 5:
        base_probs["raro"] = 0.0
        base_probs["epico"] = 0.0
        base_probs["legendario"] = 0.0
    elif nivel_hunt < 10:
        base_probs["epico"] = 0.0
        base_probs["legendario"] = 0.0
    elif nivel_hunt < 15:
        base_probs["legendario"] = 0.0
    
    # NORMALIZACIÓN AQUÍ
    total = sum(base_probs.values())
    if total > 0:
        for k in base_probs:
            base_probs[k] /= total

    # Convertir a rangos acumulativos
    acumulado = 0.0
    for tier in ["comun", "poco_comun", "raro", "epico", "legendario"]:
        prob_tier = base_probs[tier]
        if prob < acumulado + prob_tier:
            return tier
        acumulado += prob_tier

    # Fallback seguro
    return "comun"

# -----------------------------
# Simulación de 1000 loots
# -----------------------------
def simular_loots(nivel_hunt, n=50):
    resultados = Counter()
    for _ in range(n):
        tier = obtener_tier(nivel_hunt)
        resultados[tier] += 1
    return resultados

# Ejecutar simulación para nivel 5, 500 loots
sim = simular_loots(nivel_hunt=16, n=500)
print(sim)


class LootCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loot", description="Consume energía para obtener un ítem aleatorio.")
    async def loot(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        energia = obtener_energia(user_id)

        if energia is None:
            return await interaction.response.send_message("No tenés personaje.", ephemeral=True)
        if energia <= 0:
            return await interaction.response.send_message("⚠️ No te queda energía.", ephemeral=True)

        gastar_energia(user_id, 1)

        # Obtener jugador DESPUÉS de gastar energía
        jugador = db.obtener_jugador(user_id)
        nivel_hunt = jugador["lvl_caceria"]

        # Tier según hunt
        tier = obtener_tier(nivel_hunt)

        # Elegir ítem por rareza
        item = random.choice(EQUIPABLES_BY_RARITY[tier])
        tipo = item.get("tipo", "otro")

        # Equipable
        columnas = {
            "arma": "arma_equipada",
            "armadura": "armadura_equipada",
            "casco": "casco_equipado",
            "botas": "botas_equipadas"
            }
        
        columna_equipo = columnas[tipo]
        equipada_id = jugador[columna_equipo]

        nuevo_atk = item.get("stats", {}).get("ataque", 0)
        nuevo_hp  = item.get("stats", {}).get("vida", 0)

        emoji = RARITY_EMOJIS.get(tier, "🔹")

        embed = discord.Embed(
            title=f"{emoji} {item['nombre']} {emoji}",
            color=RARITY_COLORS[tier]
        )

        embed.add_field(
            name="🔖 Rareza",
            value=f"{emoji} **{tier.capitalize()}**",
            inline=False
        )

        # --------------------------
        # SIN nada equipado
        # --------------------------
        if not equipada_id:
            embed.set_footer(text="No tenés nada equipado de este tipo.")

            if nuevo_atk:
                embed.add_field(
                    name="⚔️ Daño",
                    value=(
                        f"**Objeto Actual:** —\n"
                        f"**Objeto Nuevo:** {item['nombre']} (+{nuevo_atk})"
                    ),
                    inline=False
                )

            if nuevo_hp:
                embed.add_field(
                    name="❤️ Vida",
                    value=(
                        f"**Objeto Actual:** —\n"
                        f"**Objeto Nuevo:** {item['nombre']} (+{nuevo_hp})"
                    ),
                    inline=False
                )

            view = EquiparOVender(user_id, item, slot_col=columna_equipo)
            return await interaction.response.send_message(embed=embed, view=view)


        # --------------------------
        # CON algo equipado
        # --------------------------
        equipado = EQUIPABLES_BY_ID.get(equipada_id)
        actual_atk = equipado.get("stats", {}).get("ataque", 0)
        actual_hp  = equipado.get("stats", {}).get("vida", 0)

        # Daño (solo si aplica)
        if nuevo_atk or actual_atk:
            embed.add_field(
                name="⚔️ Daño",
                value=(
                    f"**Objeto Actual:** {equipado['nombre']} (+{actual_atk})\n"
                    f"**Objeto Nuevo:** {item['nombre']} (+{nuevo_atk})"
                ),
                inline=False
            )

        # Vida (solo si aplica)
        if nuevo_hp or actual_hp:
            embed.add_field(
                name="❤️ Vida",
                value=(
                    f"**Objeto Actual:** {equipado['nombre']} (+{actual_hp})\n"
                    f"**Objeto Nuevo:** {item['nombre']} (+{nuevo_hp})"
                ),
                inline=False
            )

        view = EquiparOVender(user_id, item, slot_col=columna_equipo)
        await interaction.response.send_message(embed=embed, view=view)

def generar_loot_para_usuario(user_id, mob=None):
    jugador = db.obtener_jugador(user_id)
    nivel_hunt = jugador["lvl_caceria"]

    # Tier base según nivel
    tier = obtener_tier(nivel_hunt)

    # Ajuste de tier según mob derrotado
    if mob:
        loot_bonus = mob.get("loot_bonus", 0)
        if random.random() < loot_bonus:
            # Subir un tier de rareza si aplica
            if tier == "comun": tier = "poco_comun"
            elif tier == "poco_comun": tier = "raro"
            elif tier == "raro": tier = "epico"
            elif tier == "epico": tier = "legendario"

    # Fallback seguro si no hay ítems de esa rareza
    if tier not in EQUIPABLES_BY_RARITY or not EQUIPABLES_BY_RARITY[tier]:
        tier = "comun"

    # Elegir ítem por rareza
    item = random.choice(EQUIPABLES_BY_RARITY[tier])
    tipo = item.get("tipo", "otro")

    emoji = RARITY_EMOJIS.get(tier, "🔹")
    color = RARITY_COLORS[tier]

    embed = discord.Embed(
        title=f"{emoji} {item['nombre']} {emoji}",
        color=color
    )
    embed.add_field(
        name="🔖 Rareza",
        value=f"{emoji} **{tier.capitalize()}**",
        inline=False
    )

    # --------------------------
    # EQUIPABLES
    # --------------------------
    columnas = {
        "arma": "arma_equipada",
        "armadura": "armadura_equipada",
        "casco": "casco_equipado",
        "botas": "botas_equipadas"
    }
    columna_equipo = columnas.get(tipo, "arma_equipada")
    equipada_id = jugador[columna_equipo]

    nuevo_atk = item.get("stats", {}).get("ataque", 0)
    nuevo_hp  = item.get("stats", {}).get("vida", 0)

    # Nada equipado
    if not equipada_id:
        embed.set_footer(text="No tenés nada equipado de este tipo.")
        if nuevo_atk:
            embed.add_field(
                name="⚔️ Daño",
                value=f"**Objeto Actual:** —\n**Objeto Nuevo:** {item['nombre']} **(+{nuevo_atk})**",
                inline=False
            )
        if nuevo_hp:
            embed.add_field(
                name="❤️ Vida",
                value=f"**Objeto Actual:** —\n**Objeto Nuevo:** {item['nombre']} **(+{nuevo_hp})**",
                inline=False
            )
    # Ya hay algo equipado
    else:
        equipado = EQUIPABLES_BY_ID.get(equipada_id)
        actual_atk = equipado.get("stats", {}).get("ataque", 0)
        actual_hp  = equipado.get("stats", {}).get("vida", 0)

        if nuevo_atk or actual_atk:
            embed.add_field(
                name="⚔️ Daño",
                value=(
                    f"**Objeto Actual:** {equipado['nombre']} **(+{actual_atk})**\n"
                    f"**Objeto Nuevo:** {item['nombre']} **(+{nuevo_atk})**"
                ),
                inline=False
            )
        if nuevo_hp or actual_hp:
            embed.add_field(
                name="❤️ Vida",
                value=(
                    f"**Objeto Actual:** {equipado['nombre']} **(+{actual_hp})**\n"
                    f"**Objeto Nuevo:** {item['nombre']} **(+{nuevo_hp})**"
                ),
                inline=False
            )

    view = EquiparOVender(user_id, item, slot_col=columna_equipo)
    db.agregar_item(user_id, item["id"], 1)

    # Devolver también la experiencia que otorga el mob
    mob_exp = mob.get("mob_exp", 0) if mob else 0
    return embed, view, mob_exp


async def setup(bot):
    await bot.add_cog(LootCommand(bot))
