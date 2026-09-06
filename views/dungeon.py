import discord
from discord.ui import View, Button
from discord import Embed, ButtonStyle
from services.jugadores import obtener_jugador, sumar_oro
from services.dungeon_run import DungeonRun
from services.dungeon import obtener_dungeon, obtener_lista_dungeons, obtener_llave_dungeon
from utils import db
from views.affinity import ELEMENTS
from data.texts import descripcion_dungeon

def dungeon_intro_text(dungeons):
    """
    Genera un texto introductorio rolero y épico para la selección de dungeons.
    """
    desc = (
        "🗺️ **En el tablón de tareas** has descubierto **antiguas ruinas** dispersas por tierras olvidadas. "
        "Los rumores hablan de **tesoros ocultos**, **criaturas temibles** y **secretos milenarios**. "
        "Algunas ruinas parecen **casi impenetrables**, mientras otras dejan ver señales de aventureros previos. "
        "Cada desafío requiere **valor**, **astucia** y algo de suerte.\n\n"
        "🌟 Las ruinas disponibles para tu aventura son:\n"
    )

    for d in dungeons:
        if d['nivel_recomendado'] >= 15:
            peligro = "🔥 **Extremo**"
        elif d['nivel_recomendado'] >= 10:
            peligro = "⚔️ **Alto**"
        elif d['nivel_recomendado'] >= 6:
            peligro = "🛡️ **Moderado**"
        else:
            peligro = "🍃 **Sencillo**"

        desc += f"• **{d['nombre']}** — Nivel recomendado: **{d['nivel_recomendado']}** ({peligro})\n"

    desc += "\n✨ **Elige sabiamente** a cuál de estas aventuras te atreverás, y que la suerte de los héroes te acompañe."
    return desc

AFINIDAD_EMOJI = {e["name"]: e["emoji"] for e in ELEMENTS}
    
# ---------------------------
# Vista para seleccionar la dungeon
# ---------------------------
class DungeonSelectView(View):
    def __init__(self, leader_id: str):
        super().__init__(timeout=60)
        self.leader_id = leader_id
        self.message = None
        self.dungeons = obtener_lista_dungeons()

        # Botones por cada dungeon
        for dungeon in self.dungeons:
            label = f"{dungeon['nombre']} (Nv {dungeon['nivel_recomendado']})"
            self.add_item(DungeonButton(
                dungeon_id=dungeon["id"],
                label=label,
                leader_id=leader_id,
                style=ButtonStyle.success
            ))

        # Botón Cancelar al final
        cancelar_btn = Button(label="Cancelar", style=ButtonStyle.danger)
        cancelar_btn.callback = self.cancelar_callback  # callback manual
        self.add_item(cancelar_btn)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    embed=Embed(
                        title="⏳ Selección de dungeon vencida",
                        description="No se eligió una dungeon a tiempo. Podés iniciar otra con `/dungeon`.",
                        color=0x808080,
                    ),
                    view=self,
                )
            except discord.HTTPException:
                pass

    async def cancelar_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.leader_id:
            return await interaction.response.send_message(
                "❌ Solo el líder puede cancelar la selección.", ephemeral=True
            )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            embed=Embed(
                title="❌ Expedición cancelada",
                description="El líder decidió cancelar la selección de dungeon.",
                color=0xFF0000
            ),
            view=self
        )
        self.stop()
        
# ---------------------------
# Botón de cada dungeon en la selección
# ---------------------------
class DungeonButton(Button):
    def __init__(self, dungeon_id, label, leader_id, style):
        super().__init__(label=label, style=style)
        self.dungeon_id = dungeon_id
        self.leader_id = leader_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.leader_id:
            return await interaction.response.send_message(
                "❌ Solo el líder puede elegir la dungeon.", ephemeral=True
            )

        llave_id = obtener_llave_dungeon(self.dungeon_id)
        if not db.tiene_item(self.leader_id, llave_id):
            llave = db.obtener_item_por_id(llave_id)
            return await interaction.response.send_message(
                embed=Embed(
                    title="🔒 La entrada está sellada",
                    description=(
                        f"Para formar una expedición a **{obtener_dungeon(self.dungeon_id)['nombre']}**, "
                        f"necesitás una **{llave['nombre']}**.\n\n"
                        "La llave no se consume hasta que la expedición comienza."
                    ),
                    color=0xC0392B,
                ),
                ephemeral=True,
            )

        # Crear la dungeon real
        view = DungeonView(leader_id=self.leader_id, dungeon_id=self.dungeon_id)
        self.view.stop()

        nombre_afinidad = view.run.jugadores[0]['afinidad']  # Ej: "Fuego"
        emoji_afinidad = AFINIDAD_EMOJI.get(nombre_afinidad, "")

        afinidad_lider = f"{emoji_afinidad} {nombre_afinidad}"

        embed = Embed(
            title=f"🗝️ Dungeon: {view.dungeon['nombre']}",
            description=(
                f"{descripcion_dungeon(view.dungeon['nombre'])}\n\n"
                f"👑 **Líder:** {view.run.jugadores[0]['username']} {AFINIDAD_EMOJI.get(view.run.jugadores[0]['afinidad'], '')} — "
                "Con determinación y coraje, se prepara para guiar la expedición.\n\n"
                f"🛈 *Otros jugadores pueden unirse.*\n"
                f"🛈 *El líder puede comenzar o cancelar la dungeon.*"
            ),
            color=0xFFD700
        )

        await interaction.response.edit_message(embed=embed, view=view)
        view.message = await interaction.original_response()


# ---------------------------
# Vista de la dungeon en sí
# ---------------------------
class DungeonView(View):
    MAX_JUGADORES = 4

    def __init__(self, leader_id: str, dungeon_id: int):
        super().__init__(timeout=180)  # 2 min para unir jugadores
        self.leader_id = leader_id
        self.dungeon_id = dungeon_id
        self.run = None
        self.jugadores_ids = []
        self.message = None

        # Obtener dungeon
        dungeon = obtener_dungeon(dungeon_id)
        if dungeon is None:
            raise ValueError("Dungeon no existe")
        self.dungeon = dungeon

        # Obtener líder
        leader = obtener_jugador(str(leader_id))
        if leader is None:
            raise ValueError("Líder no registrado")

        # Pasar directamente la Row a DungeonRun
        self.run = DungeonRun(dungeon, [leader])
        self.jugadores_ids.append(leader_id)


    # ---------------------------
    # Botón Unirse
    # ---------------------------
    @discord.ui.button(label="Unirse", style=ButtonStyle.primary)
    async def unirse(self, interaction: discord.Interaction, button: Button):
        user_id = str(interaction.user.id)
        if user_id in self.jugadores_ids:
            return await interaction.response.send_message("❌ Ya estás en la dungeon.", ephemeral=True)

        jugador = obtener_jugador(user_id)
        if not jugador:
            return await interaction.response.send_message("❌ No estás registrado.", ephemeral=True)

        llave_id = obtener_llave_dungeon(self.dungeon_id)
        llave = db.obtener_item_por_id(llave_id)
        if not db.tiene_item(user_id, llave_id):
            return await interaction.response.send_message(
                embed=Embed(
                    title="🔒 No podés unirte todavía",
                    description=f"Necesitás una **{llave['nombre']}** para participar en esta expedición.",
                    color=0xC0392B,
                ),
                ephemeral=True,
            )

        if len(self.run.jugadores) >= self.MAX_JUGADORES:
            return await interaction.response.send_message("❌ La dungeon ya está llena.", ephemeral=True)

        # Agregar jugador
        self.run.agregar_jugador(jugador)
        self.jugadores_ids.append(user_id)

        jugadores_mod, eventos, oro_extra = self.run.aplicar_afinidades()
        buff_msg = ""
        if eventos:
            for e in eventos:
                if e["tipo"] in ("sinergia", "conflicto"):
                    a1, a2 = e["afinidades"]
                    tipo = "✨ Sinergia" if e["tipo"]=="sinergia" else "⚠️ Conflicto"
                    buff_msg += f"{tipo} entre **{a1}** y **{a2}** ({e['texto']})\n"
                elif e["tipo"]=="oro":
                    buff_msg += f"{e['texto']}\n"
                    
        # Embed actualizado con todos los jugadores
        jugadores_nombres = [
            f"{j['username']} {AFINIDAD_EMOJI.get(j['afinidad'], '')}"
            for j in self.run.jugadores
        ]

        embed = Embed(
            title=f"🗝️ Dungeon: {self.dungeon['nombre']}",
            description=(
                f"{descripcion_dungeon(self.dungeon['nombre'])}\n\n"
                f"👑 **Líder:** {self.run.jugadores[0]['username']} {AFINIDAD_EMOJI.get(self.run.jugadores[0]['afinidad'], '')} — "
                "Con determinación y coraje, se prepara para guiar la expedición.\n\n"
                f"🧑‍🤝‍🧑 **Jugadores unidos ({len(jugadores_nombres)-1}):** {', '.join(jugadores_nombres[1:])}\n\n"
                f"{buff_msg}\n"
                f"🛈 *Otros jugadores pueden unirse.*\n"
                f"🛈 *El líder puede comenzar o cancelar la dungeon.*"
            ),
            color=0xFFD700
        )

        await self.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"✅ {jugador['username']} se unió a la dungeon.", ephemeral=True)

    @discord.ui.button(label="Salir", style=ButtonStyle.secondary)
    async def salir(self, interaction: discord.Interaction, button: Button):
        user_id = str(interaction.user.id)
        if user_id == self.leader_id:
            return await interaction.response.send_message(
                "❌ El líder no puede salir del lobby. Puede cancelarlo.", ephemeral=True
            )
        if user_id not in self.jugadores_ids:
            return await interaction.response.send_message("❌ No estás dentro de esta dungeon.", ephemeral=True)

        self.jugadores_ids.remove(user_id)
        self.run.jugadores = [j for j in self.run.jugadores if str(j["user_id"]) != user_id]
        jugadores_nombres = [
            f"{j['username']} {AFINIDAD_EMOJI.get(j['afinidad'], '')}"
            for j in self.run.jugadores
        ]
        embed = Embed(
            title=f"🗝️ Dungeon: {self.dungeon['nombre']}",
            description=(
                f"{descripcion_dungeon(self.dungeon['nombre'])}\n\n"
                f"🔑 **Llave requerida:** {db.obtener_item_por_id(obtener_llave_dungeon(self.dungeon_id))['nombre']}\n\n"
                f"👑 **Líder:** {jugadores_nombres[0]}\n"
                f"🧑‍🤝‍🧑 **Jugadores unidos ({len(jugadores_nombres)-1}):** {', '.join(jugadores_nombres[1:]) or 'Ninguno'}\n\n"
                "🗝️ Las llaves se consumen únicamente al comenzar."
            ),
            color=0xFFD700,
        )
        await self.message.edit(embed=embed, view=self)
        await interaction.response.send_message("✅ Saliste de la expedición. Tu llave no fue consumida.", ephemeral=True)

    # ---------------------------
    # Botón Comenzar
    # ---------------------------
    @discord.ui.button(label="Comenzar", style=ButtonStyle.success)
    async def comenzar(self, interaction: discord.Interaction, button: Button):
        user_id = str(interaction.user.id)
        if user_id != self.leader_id:
            return await interaction.response.send_message("❌ Solo el líder puede comenzar la dungeon.", ephemeral=True)

        llave_id = obtener_llave_dungeon(self.dungeon_id)
        nombres_por_id = {str(j["user_id"]): j["username"] for j in self.run.jugadores}
        consumidas, faltantes = db.consumir_item_por_usuario(nombres_por_id, llave_id)
        if not consumidas:
            nombres_faltantes = ", ".join(nombres_por_id[user_id] for user_id in faltantes)
            return await interaction.response.send_message(
                embed=Embed(
                    title="🔒 La expedición no puede comenzar",
                    description=(
                        f"Falta la llave de **{nombres_faltantes}**.\n\n"
                        "Cada integrante necesita aportar su propia llave específica."
                    ),
                    color=0xC0392B,
                ),
                ephemeral=True,
            )

        resultado = self.run.resolver_combate()
        jugadores_nombres = ", ".join([j["username"] for j in self.run.jugadores])

        embed = Embed(
            title=f"Dungeon: {self.dungeon['nombre']}",
            description=(
                f"Boss: {self.run.boss['nombre']}\n"
                f"Jugadores: {jugadores_nombres}\n"
                f"Resultado: **{resultado.upper()}**\n"
                f"Oro recompensado: {self.dungeon['oro_recompensa'] if resultado=='victoria' else 0}"
            ),
            color=0x00FF00 if resultado == "victoria" else 0xFF0000
        )

        # Reparto de oro si hay victoria
        if resultado == "victoria":
            bonus = self.run.calcular_bonus_oro()
            oro_total = self.dungeon["oro_recompensa"]
            oro_total = int(oro_total * (1 + bonus))

            num_jugadores = len(self.run.jugadores)
            oro_por_jugador = oro_total // num_jugadores

            detalle_oro = []
            for jugador in self.run.jugadores:
                jugador_id = jugador["user_id"]
                sumar_oro(jugador_id, oro_por_jugador)
                detalle_oro.append(f"{jugador['username']}: {oro_por_jugador}💰")

            embed.description += "\n\nOro recibido por jugador:\n" + "\n".join(detalle_oro)

        # Deshabilitar botones
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

        await interaction.response.send_message(embed=embed, ephemeral=False)
        self.stop()

    # ---------------------------
    # Botón Cancelar
    # ---------------------------
    @discord.ui.button(label="Cancelar", style=ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.leader_id:
            return

        embed = Embed(
            title="Dungeon cancelada",
            description="El líder decidió cancelar la dungeon.",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)
        self.stop()

    # ---------------------------
    # Timeout
    # ---------------------------
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(
                    embed=Embed(
                        title="Dungeon expirada",
                        description="El tiempo para unir jugadores se acabó.",
                        color=0xFF0000
                    ),
                    view=self
                )
            except:
                pass
