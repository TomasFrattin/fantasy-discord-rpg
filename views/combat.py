# views/combat.py
import random
from discord.ui import View, button, Button
from discord import ButtonStyle, Interaction, Embed
from services.jugadores import obtener_jugador, actualizar_vida, sumar_oro
from utils.combat_manager import create_combat, get_combat, delete_combat
from commands.hunt import agregar_exp_caceria

DEFEAT_DESCS = [
    "El pez te venció y escapó.", 
    "¡Perdiste! El pez se zambulló y te humilló."
]

ESCAPE_CONFIG = {
    "probabilidad": 0.4,
    "mensajes_exito": ["Lograste soltar al pez."],
    "mensajes_fallo": ["El pez se resiste y te lastima."]
}

class CombatView(View):
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

        jugador = obtener_jugador(self.user_id)
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
            actualizar_vida(self.user_id, combate["player_hp"])
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
            sumar_oro(self.user_id, -obtener_jugador(self.user_id)["oro"])
            actualizar_vida(self.user_id, 1)
            delete_combat(self.user_id)
            desc = random.choice(DEFEAT_DESCS)
            embed.add_field(name="🪦 Derrota", value=desc, inline=False)
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])
            return

        # --- Victoria ---
        if combate["mob_hp"] <= 0:
            embed.title += "\n🏆 Victoria"
            embed.color = 0x00FF00

            exp_ganada = combate.get("mob_exp", 0)
            oro_ganado = combate.get("mob_valor_oro", 0)  # puedes poner un valor real de oro
            sumar_oro(self.user_id, oro_ganado)

            resultado = agregar_exp_caceria(self.user_id, exp_ganada)
            if resultado:
                nuevo_lvl, exp_restante, niveles_subidos = resultado
                if niveles_subidos > 0:
                    embed.add_field(
                        name="⭐ Experiencia",
                        value=f"Ganaste **{exp_ganada} XP** y subiste {niveles_subidos} nivel(es)! Ahora sos nivel **{nuevo_lvl}**.\n\n💰 Ganaste **{oro_ganado} de oro**",
                        inline=False
                    )
                else:
                    exp_necesaria = int(150 * (nuevo_lvl ** 1.3))
                    embed.add_field(
                        name="⭐ Experiencia",
                        value=f"Ganaste **{exp_ganada} XP**.\nProgreso: **{exp_restante}/{exp_necesaria} XP**\n\n💰 **Ganaste** **{oro_ganado} de oro**",
                        inline=False
                    )

            delete_combat(self.user_id)
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])
            return

        # Continuar combate
        create_combat(self.user_id, combate)
        await interaction.response.edit_message(embed=embed, view=self, attachments=[])
        
    @button(label="Huir", style=ButtonStyle.danger)
    async def huir(self, interaction: Interaction, button: Button):
        combate = get_combat(self.user_id)
        if not combate:
            return await interaction.response.send_message("El combate ya no está activo.", ephemeral=True)

        exito = random.random() < 0.4
        embed = Embed(
            title="🏃‍♂️ ¡Has escapado!" if exito else "❌ ¡No pudiste huir!",
            description="Huiste del combate." if exito else "El pez te golpea al intentar huir.",
            color=0x00FF00 if exito else 0xFF4500
        )
        if not exito:
            daño_mob = int(combate["mob_atk"] * random.uniform(0.95,1.05))
            combate["player_hp"] -= daño_mob
            if combate["player_hp"] < 0:
                combate["player_hp"] = 0
            actualizar_vida(self.user_id, combate["player_hp"])
            create_combat(self.user_id, combate)
            embed.add_field(name=f"💀 {combate['mob_nombre']}", value=f"HP: **{combate['mob_hp']}/{combate['mob_hp_max']}**", inline=False)
            embed.add_field(name="🧍 Jugador", value=f"HP: **{combate['player_hp']}/{combate['player_hp_max']}**", inline=False)
        else:
            delete_combat(self.user_id)

        await interaction.response.edit_message(embed=embed, view=None, attachments=[])
