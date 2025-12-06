import random
import discord
from discord.ui import View, Button
from utils import db
from commands.loot import LootCommand  # tu función de loot ya creada
from data.texts import DEFEAT_DESCS

class CombatView(View):
    def __init__(self, combat_payload, user_id):
        super().__init__(timeout=60)
        self.combat = combat_payload
        self.user_id = user_id

    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este combate.", ephemeral=True)

        # --- Ataque del jugador ---
        player_atk = random.randint(1, 10)  # o usar stats del jugador
        mob_def = int(self.combat["mob_hp_max"] * 0.02)  # defensa del mob 2% de max HP
        daño_jugador = player_atk - mob_def
        daño_jugador = max(daño_jugador, 0)

        fallo_jugador = False
        if random.random() < 0.1:  # 10% de fallar
            daño_jugador = 0
            fallo_jugador = True

        self.combat["mob_hp"] -= daño_jugador
        if self.combat["mob_hp"] < 0:
            self.combat["mob_hp"] = 0

        # --- Ataque del mob (solo si sigue vivo) ---
        daño_mob = 0
        fallo_mob = False
        if self.combat["mob_hp"] > 0:
            mob_atk = self.combat["mob_atk"]
            player_def = int(self.combat["player_hp_max"] * 0.02)
            daño_mob = mob_atk - player_def
            daño_mob = max(daño_mob, 0)
            if random.random() < 0.1:
                daño_mob = 0
                fallo_mob = True
            self.combat["player_hp"] -= daño_mob
            if self.combat["player_hp"] < 0:
                self.combat["player_hp"] = 0

        # --- Construir embed ---
        embed = discord.Embed(
            title=f"⚔️ Combate vs {self.combat['mob_emoji']} {self.combat['mob_nombre']}",
            color=0xFF4500
        )

        embed.add_field(
            name=f"💀 {self.combat['mob_nombre']}",
            value=f"HP: **{self.combat['mob_hp']}/{self.combat['mob_hp_max']}**",
            inline=False
        )

        embed.add_field(
            name=f"🧍 Jugador",
            value=f"HP: **{self.combat['player_hp']}/{self.combat['player_hp_max']}**",
            inline=False
        )

        # Mensajes del turno
        turno_msg = ""
        if fallo_jugador:
            turno_msg += f"⚠️ Fallaste tu ataque!\n"
        else:
            turno_msg += f"🗡️ Le hiciste **{daño_jugador}** de daño.\n"

        if self.combat["mob_hp"] > 0:
            if fallo_mob:
                turno_msg += f"⚠️ {self.combat['mob_nombre']} falló su ataque!\n"
            else:
                turno_msg += f"💥 {self.combat['mob_nombre']} te hizo **{daño_mob}** de daño.\n"

        embed.description = turno_msg

        # --- Chequear resultados ---
        if self.combat["player_hp"] <= 0:
            embed.title += " ❌ Derrota"
            embed.color = 0x8B0000
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=None)
            return

        if self.combat["mob_hp"] <= 0:
            embed.title += " 🏆 Victoria"
            embed.color = 0x00FF00
            # Llamar loot
            loot = LootCommand(self.user_id)  # tu función loot
            embed.description += f"\n🎁 Obteniste: {loot}"
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=None)
            return

        await interaction.response.edit_message(embed=embed)
