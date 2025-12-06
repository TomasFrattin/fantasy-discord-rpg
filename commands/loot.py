# commands/loot.py
import random
import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from data_loader import EQUIPABLES, EQUIPABLES_BY_ID
from views.equip import EquiparOVender

RARITY_COLORS = {
    "comun": 0xB0B0B0,
    "raro": 0x3A82F7,
    "epico": 0xA335EE,
    "legendario": 0xFF8000
}

RARITY_EMOJIS = {
    "comun": "🔹",
    "raro": "🔷",
    "epico": "💜",
    "legendario": "🔥"
}

EQUIPABLES_BY_RARITY = {}
for item in EQUIPABLES:
    r = item.get("rareza", "comun")
    EQUIPABLES_BY_RARITY.setdefault(r, []).append(item)

def obtener_tier():
    prob = random.random()
    if prob < 0.60: return "comun"
    if prob < 0.85: return "raro"
    if prob < 0.97: return "epico"
    return "legendario"


class LootCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="loot", description="Consume energía para obtener un ítem aleatorio.")
    async def loot(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        energia = db.obtener_energia(user_id)

        if energia is None:
            return await interaction.response.send_message("No tenés personaje.", ephemeral=True)
        if energia <= 0:
            return await interaction.response.send_message("⚠️ No te queda energía.", ephemeral=True)

        db.gastar_energia(user_id, 1)

        tier = obtener_tier()
        item = random.choice(EQUIPABLES_BY_RARITY[tier])
        tipo = item.get("tipo", "otro")
        jugador = db.obtener_jugador(user_id)

        # Consumible → no equipable
        if tipo not in ("arma", "armadura", "casco", "botas"):
            db.agregar_consumible(user_id, item["id"])

            emoji = RARITY_EMOJIS.get(tier, "🔹")

            embed = discord.Embed(
                title=f"{emoji} {item['nombre']} {emoji}",
                description=(
                    f"**Tipo:** {tipo.capitalize()}\n"
                    f"**Rareza:** {emoji} **{tier.capitalize()}**"
                ),
                color=RARITY_COLORS[tier]
            )

            embed.set_footer(text=f"⚡ Energía restante: {db.obtener_energia(user_id)}")

            return await interaction.response.send_message(embed=embed)

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

def generar_loot_para_usuario(user_id):
    tier = obtener_tier()
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

    if tipo not in ("arma", "armadura", "casco", "botas"):
        db.agregar_consumible(user_id, item["id"])
        embed.description = (
            f"**Tipo:** {tipo.capitalize()}\n"
            f"**Rareza:** {emoji} **{tier.capitalize()}**"
        )
        return embed, None  # No hay vista para consumibles

    # Equipable
    jugador = db.obtener_jugador(user_id)
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
    else:
        from data_loader import EQUIPABLES_BY_ID
        equipado = EQUIPABLES_BY_ID.get(equipada_id)
        actual_atk = equipado.get("stats", {}).get("ataque", 0)
        actual_hp  = equipado.get("stats", {}).get("vida", 0)
        if nuevo_atk or actual_atk:
            embed.add_field(
                name="⚔️ Daño",
                value=(
                    f"**Objeto Actual:** {equipado['nombre']} (+{actual_atk})\n"
                    f"**Objeto Nuevo:** {item['nombre']} (+{nuevo_atk})"
                ),
                inline=False
            )
        if nuevo_hp or actual_hp:
            embed.add_field(
                name="❤️ Vida",
                value=(
                    f"**Objeto Actual:** {equipado['nombre']} (+{actual_hp})\n"
                    f"**Objeto Nuevo:** {item['nombre']} (+{nuevo_hp})"
                ),
                inline=False
            )
    from views.equip import EquiparOVender
    view = EquiparOVender(user_id, item, slot_col=columna_equipo)
    db.agregar_item(user_id, item["id"], 1)
    return embed, view

async def setup(bot):
    await bot.add_cog(LootCommand(bot))
