import random
import discord
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, button, Button
from utils import db
from utils.combat_manager import create_combat, get_combat, delete_combat, has_combat
import logging
from data.texts import DEFEAT_DESCS, ESCAPE_CONFIG
from utils.messages import mensaje_usuario_no_creado, mensaje_sin_energia, mensaje_accion_en_progreso
from PIL import Image
import os
from commands.loot import generar_loot_para_usuario
from data_loader import MOBS
from utils.helpers import preparar_imagen_mob
from services.jugador import sumar_oro
# -----------------------------
# Funciones auxiliares
# -----------------------------

def elegir_mob(nivel_hunt: int) -> dict:
    """Elige un mob según lvl_caceria y probabilidades de tier."""
    if nivel_hunt < 5:
        tiers = ["comun", "poco_comun"]
    elif nivel_hunt < 10:
        tiers = ["comun", "poco_comun", "raro"]
    else:
        tiers = ["comun", "poco_comun", "raro", "epico"]
    
    mobs_filtrados = [m for m in MOBS if m.get("tier","comun") in tiers]

        # Chance de que aparezca un mob legendario
    if random.random() < 0.02:  # 2% de probabilidad
        mobs_filtrados = [m for m in MOBS if m.get("tier") == "legendario"]

    return random.choice(mobs_filtrados)


def agregar_exp_caceria(user_id, exp_obtenida):
    jugador = db.obtener_jugador(user_id)
    exp_actual = jugador["exp_caceria"] or 0
    lvl = jugador["lvl_caceria"] or 1

    exp_actual += exp_obtenida
    niveles_subidos = 0

    # Umbral dinámico: 150 * (lvl ** 1.3)
    while exp_actual >= int(150 * (lvl ** 1.3)):
        exp_actual -= 100 * lvl
        lvl += 1
        niveles_subidos += 1

    db.actualizar_exp_caceria(user_id, exp_actual)
    db.actualizar_lvl_caceria(user_id, lvl)

    return lvl, exp_actual, niveles_subidos

# -----------------------------
# Vista del combate
# -----------------------------
class HuntView(View):
    def __init__(self, user_id: str):
        super().__init__(timeout=60)
        self.user_id = user_id

    @button(label="Atacar", style=ButtonStyle.primary)
    async def atacar(self, interaction: Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        combate = get_combat(self.user_id)
        if not combate:
            return await interaction.response.send_message("El combate ya no está activo.", ephemeral=True)

        jugador = db.obtener_jugador(self.user_id)
        player_atk = jugador["damage"]

        # --- Ataque jugador ---
        mob_def = int(combate["mob_hp_max"] * 0.02)
        daño_jugador = int(max(player_atk * random.uniform(0.95, 1.05) - mob_def, 0))
        fallo_jugador = random.random() < 0.1
        if fallo_jugador:
            daño_jugador = 0

        combate["mob_hp"] -= daño_jugador
        if combate["mob_hp"] < 0:
            combate["mob_hp"] = 0

        # --- Ataque mob ---
        daño_mob = 0
        fallo_mob = False
        if combate["mob_hp"] > 0:
            mob_atk = combate["mob_atk"]
            player_def = int(combate["player_hp_max"] * 0.02)
            daño_mob = int(max(mob_atk * random.uniform(0.95,1.05) - player_def,0))
            fallo_mob = random.random() < 0.1
            if fallo_mob:
                daño_mob = 0
            combate["player_hp"] -= daño_mob
            db.actualizar_vida(self.user_id, combate["player_hp"])
            if combate["player_hp"] < 0:
                combate["player_hp"] = 0

        # --- Embed ---
        embed = Embed(
            title=f"⚔️ Combate vs {combate['mob_emoji']} {combate['mob_nombre']}",
            color=0xFF4500
        )

        embed.add_field(
            name=f"💀 {combate['mob_nombre']}",
            value=f"HP: **{combate['mob_hp']}/{combate['mob_hp_max']}**",
            inline=False
        )
        embed.add_field(
            name="🧍 Jugador",
            value=f"HP: **{combate['player_hp']}/{combate['player_hp_max']}**",
            inline=False
        )

        turno_msg = ""
        if fallo_jugador:
            turno_msg += "⚠️ Fallaste tu ataque!\n"
        else:
            turno_msg += f"🗡️ Le hiciste **{daño_jugador}** de daño.\n"
        if combate["mob_hp"] > 0:
            if fallo_mob:
                turno_msg += f"⚠️ {combate['mob_nombre']} falló su ataque!\n"
            else:
                turno_msg += f"💥 {combate['mob_nombre']} te hizo **{daño_mob}** de daño.\n"
        embed.description = turno_msg

        # --- Derrota ---
        if combate["player_hp"] <= 0:
            embed.title += "\n❌ Derrota"
            embed.color = 0x8B0000
            sumar_oro(self.user_id, -db.obtener_jugador(self.user_id)["oro"])
            db.actualizar_vida(self.user_id, max(1,jugador["vida_max"]//2))
            db.gastar_energia(self.user_id, jugador["energia"])
            delete_combat(self.user_id)
            desc = random.choice(DEFEAT_DESCS)
            embed.add_field(name="🪦 Derrota",
                            value=f"{desc}\n\nPerdiste todo tu oro y estás exhausto 😓", inline=False)
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])
            return

        # --- Victoria ---
        if combate["mob_hp"] <= 0:
            embed.title += "\n🏆 Victoria"
            embed.color = 0x00FF00

            exp_ganada = combate.get("mob_exp", 0)
            resultado = agregar_exp_caceria(self.user_id, exp_ganada)

            if resultado:
                nuevo_lvl, exp_restante, niveles_subidos = resultado

                if niveles_subidos > 0:
                    embed.add_field(
                        name="⭐ Experiencia",
                        value=(
                            f"Has ganado **{exp_ganada} XP**.\n"
                            f"¡Subiste {niveles_subidos} nivel(es)! Ahora sos nivel **{nuevo_lvl}**."
                        ),
                        inline=False
                    )
                else:
                    exp_necesaria = int(150 * (nuevo_lvl ** 1.3))
                    embed.add_field(
                        name="⭐ Experiencia",
                        value=(
                            f"Has ganado **{exp_ganada} XP**.\n"
                            f"Progreso: **{exp_restante}/{exp_necesaria} XP**"
                        ),
                        inline=False
                    )
                    
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])

            loot_embed, loot_view, mob_exp = generar_loot_para_usuario(self.user_id, combate)

            delete_combat(self.user_id)

            await interaction.followup.send(embed=loot_embed, view=loot_view, ephemeral=True)
            return

        # Continuar combate
        create_combat(self.user_id, combate)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])


    async def intentar_huir(self, interaction: Interaction):
        combate = get_combat(self.user_id)
        if not combate:
            return await interaction.response.send_message("El combate ya no está activo.", ephemeral=True)

        exito = random.random() <= ESCAPE_CONFIG["probabilidad"]
        if exito:
            mensaje = random.choice(ESCAPE_CONFIG["mensajes_exito"])
            delete_combat(self.user_id)
            embed = Embed(
                title="🏃‍♂️ ¡Has escapado!",
                description=mensaje,
                color=0x00FF00
            )
            embed.add_field(
                name=f"💀 {combate['mob_nombre']}",
                value=f"HP: **{combate['mob_hp']}/{combate['mob_hp_max']}**",
                inline=False
            )
            embed.add_field(
                name=f"🧍 Jugador",
                value=f"HP: **{combate['player_hp']}/{combate['player_hp_max']}**",
                inline=False
            )
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])
            return

        # Falló el escape: el mob ataca automáticamente
        mob_atk = combate["mob_atk"]
        player_def = int(combate["player_hp_max"] * 0.02)
        daño_mob = int(max(mob_atk * random.uniform(0.95, 1.05) - player_def, 0))
        fallo_mob = random.random() < 0.1
        if fallo_mob:
            daño_mob = 0

        combate["player_hp"] -= daño_mob
        if combate["player_hp"] < 0:
            combate["player_hp"] = 0
        db.actualizar_vida(self.user_id, combate["player_hp"])

        # Embed de fallo con estilo de combate
        mensaje = random.choice(ESCAPE_CONFIG["mensajes_fallo"])
        embed = Embed(
            title="❌ ¡No pudiste huir!",
            description=f"{mensaje}\n💥 {combate['mob_nombre']} te hizo **{daño_mob}** de daño.",
            color=0xFF4500
        )

        # Nunca se debe mostrar de nuevo
        combate["image_shown"] = True

        embed.add_field(
            name=f"💀 {combate['mob_nombre']}",
            value=f"HP: **{combate['mob_hp']}/{combate['mob_hp_max']}**",
            inline=False
        )
        embed.add_field(
            name=f"🧍 Jugador",
            value=f"HP: **{combate['player_hp']}/{combate['player_hp_max']}**",
            inline=False
        )

        # Guardar estado y mantener vista
        create_combat(self.user_id, combate)
        await interaction.response.edit_message(embed=embed, view=self)

    @button(label="Huir", style=ButtonStyle.danger)
    async def huir(self, interaction: Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        await self.intentar_huir(interaction)

    @button(label="Items WIP", style=ButtonStyle.secondary, disabled=True)
    async def items_combate(self, interaction: Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        await self.intentar_huir(interaction)


# -----------------------------
# Comando hunt
# -----------------------------
class HuntCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hunt", description="Buscar un enemigo para combatir (gasta 1 energía).")
    async def hunt(self, interaction: Interaction):
        user_id = str(interaction.user.id)
        jugador = db.obtener_jugador(user_id)
        if not jugador:
            return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)
        
        energia = db.obtener_energia(user_id)
        if energia <= 0:
            return await interaction.response.send_message(embed=mensaje_sin_energia(), ephemeral=True)
        
        if db.obtener_accion_actual(user_id) or has_combat(user_id):
            return await interaction.response.send_message(embed=mensaje_accion_en_progreso(user_id), ephemeral=True)

        db.gastar_energia(user_id, 1)
        logging.info(f"[HUNT] Usuario {user_id} gastó 1 energía.")

        # Elegir mob según lvl_caceria
        mob = elegir_mob(jugador["lvl_caceria"])
        mob_hp = int(mob["vida_max"] * random.uniform(0.96,1.04))

        combat_payload = {
            "mob_id": mob["id"],
            "mob_nombre": mob["nombre"],
            "mob_emoji": mob.get("emoji",""),
            "mob_hp": mob_hp,
            "mob_hp_max": mob_hp,
            "mob_atk": mob["ataque"],
            "mob_exp": mob["exp"],
            "mob_loot_bonus": mob.get("loot_bonus",0),
            "player_hp": jugador["vida"],
            "player_hp_max": jugador["vida_max"],
            "image_shown": False,
        }
        create_combat(user_id, combat_payload)

        embed = Embed(
            title=f"{mob.get('emoji','')} ¡Has encontrado un enemigo! {mob.get('emoji','')}",
            description=f"Te topaste con **{mob['nombre']}**. ¿Qué harás?",
            color=0xA335EE
        )

        embed.add_field(name=f"📊 Estadísticas de {mob['nombre']}", value="\n", inline=False)
        embed.add_field(name="🔴 Vida", value=f"**{mob_hp}/{mob_hp}**", inline=True)
        embed.add_field(name="⚔️ Ataque", value=f"**{mob['ataque']}**", inline=True)
        embed.add_field(name=f"📊 Estadísticas de {jugador['username']}", value="\n", inline=False)
        embed.add_field(name="🧍 Vida", value=f"**{jugador['vida']}/{jugador['vida_max']}**", inline=True)
        embed.add_field(name="🗡️ Daño", value=f"**{jugador['damage']}**", inline=True)

        view = HuntView(user_id)
        mob_img_path = preparar_imagen_mob(mob["url"], size=(280,280))
        if mob_img_path:
            file = discord.File(mob_img_path, filename=os.path.basename(mob_img_path))
            embed.set_image(url=f"attachment://{os.path.basename(mob_img_path)}")
            await interaction.response.send_message(embed=embed, view=view, file=file)
            try: os.remove(mob_img_path)
            except: pass
        else:
            await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(HuntCommand(bot))