# commands/hunt.py
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

# Pool simple inicial de mobs (expandible)
MOBS = MOBS = [
    {"id": "slime", "nombre": "Slime", "vida_max": 20, "ataque": 3, "emoji": "🫧",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\slime.png"},
    {"id": "lobo", "nombre": "Lobo Salvaje", "vida_max": 35, "ataque": 5, "emoji": "🐺",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\lobo.png"},
    {"id": "bandido", "nombre": "Bandido Errante", "vida_max": 40, "ataque": 6, "emoji": "🗡️",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\bandido.png"},
    {"id": "espiritu", "nombre": "Espíritu Menor", "vida_max": 28, "ataque": 4, "emoji": "👻",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\espiritu.png"},
    {"id": "goblin", "nombre": "Goblin Travieso", "vida_max": 22, "ataque": 4, "emoji": "👹",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\goblin.png"},
    {"id": "troll", "nombre": "Troll de las Cavernas", "vida_max": 60, "ataque": 8, "emoji": "🪨",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\troll.png"},
    {"id": "vampiro", "nombre": "Vampiro Sombrío", "vida_max": 45, "ataque": 7, "emoji": "🧛",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\vampiro.png"},
    {"id": "espectro", "nombre": "Espectro Errante", "vida_max": 30, "ataque": 5, "emoji": "👻",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\espectro.png"},
    {"id": "hiena", "nombre": "Hiena Hambrienta", "vida_max": 33, "ataque": 5, "emoji": "🦝",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\hiena.png"},
    {"id": "gnomo", "nombre": "Gnomo Pícaro", "vida_max": 18, "ataque": 3, "emoji": "🧝‍♂️",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\gnomo.png"},
    {"id": "dragoncillo", "nombre": "Dragoncillo", "vida_max": 50, "ataque": 9, "emoji": "🐉",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\dragoncillo.png"},
    {"id": "momia", "nombre": "Momia Antiguo", "vida_max": 40, "ataque": 6, "emoji": "🪦",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\momia.png"},
    {"id": "serpiente", "nombre": "Serpiente Venenosa", "vida_max": 25, "ataque": 4, "emoji": "🐍",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\serpiente.png"},
    {"id": "minotauro", "nombre": "Minotauro", "vida_max": 55, "ataque": 8, "emoji": "🐂",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\minotauro.png"},
    {"id": "hechicero", "nombre": "Hechicero Errante", "vida_max": 38, "ataque": 7, "emoji": "🧙",
     "url": "C:\\Users\\Tomas\\Downloads\\mobs\\hechicero.png"},
]

def preparar_imagen_mob(ruta, size=(300, 300)):
    img = Image.open(ruta).convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)

    # cuadro blanco o transparente
    fondo = Image.new("RGBA", size, (0, 0, 0, 0))

    # centrar imagen
    offset = ((size[0] - img.width)//2, (size[1] - img.height)//2)
    fondo.paste(img, offset, img)

    output_path = f"data/temp/temp_mob_{os.path.basename(ruta)}"
    fondo.save(output_path)

    return output_path

def elegir_mob() -> dict:
    """Elige un mob aleatorio (posible lugar para tier/probabilidades)."""
    return random.choice(MOBS)


class HuntView(View):
    def __init__(self, user_id: str):
        super().__init__(timeout=60)  # expira en 60s
        self.user_id = user_id

    @button(label="Atacar", style=ButtonStyle.primary)
    async def atacar(self, interaction: Interaction, button: Button):
        if str(interaction.user.id) != self.user_id:
            return await interaction.response.send_message("No podés usar este menú.", ephemeral=True)

        combate = get_combat(self.user_id)
        if not combate:
            return await interaction.response.send_message("El combate ya no está activo.", ephemeral=True)

        import random
        # --- Ataque del jugador ---
        jugador = db.obtener_jugador(self.user_id)
        player_atk = jugador["damage"]

        mob_def = int(combate["mob_hp_max"] * 0.02)
        daño_jugador = int(max(player_atk * random.uniform(0.95, 1.05) - mob_def, 0))
        fallo_jugador = random.random() < 0.1
        if fallo_jugador:
            daño_jugador = 0

        combate["mob_hp"] -= daño_jugador
        if combate["mob_hp"] < 0:
            combate["mob_hp"] = 0

        # --- Ataque del mob (si sigue vivo) ---
        daño_mob = 0
        fallo_mob = False
        if combate["mob_hp"] > 0:
            mob_atk = combate["mob_atk"]
            player_def = int(combate["player_hp_max"] * 0.02)
            daño_mob = int(max(mob_atk * random.uniform(0.95, 1.05) - player_def, 0))
            fallo_mob = random.random() < 0.1
            if fallo_mob:
                daño_mob = 0
            combate["player_hp"] -= daño_mob
            db.actualizar_vida(self.user_id, combate["player_hp"])
            if combate["player_hp"] < 0:
                combate["player_hp"] = 0

        # --- Construir embed ---
        embed = Embed(
            title=f"⚔️ Combate vs {combate['mob_emoji']} {combate['mob_nombre']}",
            color=0xFF4500
        )

        # No mostrar imagen más veces
        # Si no querés que se muestre nunca más, simplemente no hacemos nada aquí.
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

        turno_msg = ""
        if fallo_jugador:
            turno_msg += f"⚠️ Fallaste tu ataque!\n"
        else:
            turno_msg += f"🗡️ Le hiciste **{daño_jugador}** de daño.\n"

        if combate["mob_hp"] > 0:
            if fallo_mob:
                turno_msg += f"⚠️ {combate['mob_nombre']} falló su ataque!\n"
            else:
                turno_msg += f"💥 {combate['mob_nombre']} te hizo **{daño_mob}** de daño.\n"

        embed.description = turno_msg

        # --- Chequear resultados ---
        if combate["player_hp"] <= 0:
            embed.title += "\n❌ Derrota"
            embed.color = 0x8B0000
            # Perder todo el oro
            db.sumar_oro(self.user_id, -db.obtener_jugador(self.user_id)["oro"])
            jugador = db.obtener_jugador(self.user_id)
            vida_max = jugador["vida_max"]
            db.actualizar_vida(self.user_id, max(1, vida_max // 2))  # Deja la vida a la mitad, mínimo 1

            # Poner energía a 0 al morir
            energia_actual = jugador["energia"]
            db.gastar_energia(self.user_id, energia_actual)

            delete_combat(self.user_id)
            desc = random.choice(DEFEAT_DESCS)
            embed.add_field(
                name="🪦 Derrota",
                value=f"{desc}\n\nAl incorporarte, notas que perdiste todo tu oro 💰 y sientes un gran cansancio. 😓",
                inline=False
            )       
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])
            return

        if combate["mob_hp"] <= 0:
            embed.title += "\n🏆 Victoria"
            embed.color = 0x00FF00
            delete_combat(self.user_id)
            # Llamar función de loot y mostrar resultado
            from commands.loot import generar_loot_para_usuario
            loot_embed, loot_view = generar_loot_para_usuario(self.user_id)
            await interaction.response.edit_message(embed=embed, view=None, attachments=[])
            # Enviar loot como nuevo mensaje (no ephemeral, para que pueda interactuar)
            await interaction.followup.send(embed=loot_embed, view=loot_view, ephemeral=True)
            return

        # Si sigue el combate, actualiza el mensaje y guarda el estado
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


class HuntCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hunt", description="Buscar un enemigo para combatir (gasta 1 energía).")
    async def hunt(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        # Verificar personaje y energía
        row = db.obtener_jugador(user_id)
        if not row:
            return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)
        energia = db.obtener_energia(user_id)
        if energia <= 0:
            return await interaction.response.send_message(embed=mensaje_sin_energia(), ephemeral=True)

        # Si ya tiene un combate activo, avisar
        if has_combat(user_id):
            return await interaction.response.send_message(embed=mensaje_accion_en_progreso(), ephemeral=True)


        # Gastar energía
        db.gastar_energia(user_id, 1)
        logging.info(f"[HUNT] Usuario {user_id} ha gastado 1 energía para cazar.")
        # Elegir mob y crear estado de combate
        mob = elegir_mob()
        logging.info(f"[HUNT] Usuario {user_id} ha encontrado un mob: {mob['nombre']} (ID: {mob['id']}).")
        
        jugador = db.obtener_jugador(user_id)
        player_hp = int(jugador["vida"])  # vida actual

        factor_vida = random.uniform(0.96, 1.04)

        mob_hp = int(mob["vida_max"] * factor_vida)

        combat_payload = {
            "mob_id": mob["id"],
            "mob_nombre": mob["nombre"],
            "mob_emoji": mob.get("emoji", ""),
            "mob_hp": mob_hp,
            "mob_hp_max": mob_hp,
            "mob_atk": mob["ataque"],
            "player_hp": player_hp,
            "player_hp_max": int(jugador["vida_max"]),
            "image_shown": False,
        }
        create_combat(user_id, combat_payload)

        embed = Embed(
            title=f"{mob.get('emoji','')} ¡Has encontrado un enemigo! {mob.get('emoji','')}",
            description=f"Se ha topado con **{mob['nombre']}**. ¿Qué harás?",
            color=0xA335EE
        )

        # Subtítulo: Estadísticas del enemigo
        embed.add_field(name=f"📊 Estadísticas de **{mob['nombre']}**", value="\n", inline=False)
        embed.add_field(name="🔴 Vida", value=f"**{mob_hp} / {mob_hp}**", inline=True)
        embed.add_field(name="⚔️ Ataque", value=f"**{mob['ataque']}**", inline=True)

        # Subtítulo: Estadísticas del jugador
        embed.add_field(name=f"📊 Estadísticas de **{jugador['username']}**", value="\n", inline=False)
        embed.add_field(name="🧍 Vida", value=f"**{jugador['vida']} / {jugador['vida_max']}**", inline=True)
        embed.add_field(name="🗡️ Daño", value=f"**{jugador['damage']}**", inline=True)

        view = HuntView(user_id)
        mob_img_path = preparar_imagen_mob(mob["url"], size=(280, 280))

        if mob_img_path:
            file = discord.File(mob_img_path, filename=os.path.basename(mob_img_path))
            embed.set_image(url=f"attachment://{os.path.basename(mob_img_path)}")

            await interaction.response.send_message(embed=embed, view=view, file=file)

            # eliminar archivo temporal
            try:
                os.remove(mob_img_path)
            except:
                pass

        else:
            await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(HuntCommand(bot))
