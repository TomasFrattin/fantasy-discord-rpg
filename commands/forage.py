from discord import File, app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from data.texts import RECOLECTAR_DESCRIPTIONS
import random
import os
from PIL import Image
from utils.messages import mensaje_usuario_no_creado, mensaje_sin_energia, mensaje_accion_en_progreso
from utils.helpers import crear_collage

class ForageCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="forage",
        description="Gastas 1 energía y recolectás materiales."
    )
    async def forage(self, interaction: Interaction):
        user_id = str(interaction.user.id)

        jugador = db.obtener_jugador(user_id)
        if not jugador:
            return await interaction.response.send_message(embed=mensaje_usuario_no_creado(), ephemeral=True)

        energia = db.obtener_energia(user_id)
        if energia <= 0:
            return await interaction.response.send_message(embed=mensaje_sin_energia(), ephemeral=True)

        accion = db.obtener_accion_actual(user_id)
        if accion:
            return await interaction.response.send_message(embed=mensaje_accion_en_progreso(user_id), ephemeral=True)
        
        db.gastar_energia(user_id, 1)

        try:
            resultados = db.recolectar_materiales(user_id)
            if not resultados:
                return await interaction.response.send_message(
                    "No conseguiste ningún material esta vez.",
                    ephemeral=True
                )

            texto_flavor = random.choice(RECOLECTAR_DESCRIPTIONS)

            # Agrupar duplicados
            agrupados = {}
            for item_id, nombre, cantidad in resultados:
                if item_id not in agrupados:
                    agrupados[item_id] = {"nombre": nombre, "cantidad": 0}
                agrupados[item_id]["cantidad"] += cantidad

            # ---------- CÁLCULO DE EXP ----------
            exp_total = 0
            for item_id, nombre, cantidad in resultados:
                item = db.obtener_item_por_id(item_id)
                rareza = item["rareza"] or "comun"

                if rareza == "comun":
                    exp_total += 5 * cantidad
                elif rareza == "raro":
                    exp_total += 12 * cantidad
                elif rareza == "epico":
                    exp_total += 25 * cantidad
                else:
                    exp_total += 45 * cantidad

            nuevo_lvl, exp_restante, niveles_subidos = db.agregar_exp_recoleccion(user_id, exp_total)
            # -----------------------------------

            embed = Embed(
                title="🧺 Recolección completada",
                description=texto_flavor,
                color=0x00ff00
            )

            # Items obtenidos
            for item_id, info in agrupados.items():
                embed.add_field(
                    name=info["nombre"],
                    value=f"Cantidad: × {info['cantidad']}",
                    inline=True
                )

            # EXP
            if niveles_subidos > 0:
                embed.add_field(
                    name="⭐ Experiencia",
                    value=(
                        f"Ganaste **{exp_total} XP**.\n"
                        f"¡Subiste {niveles_subidos} nivel(es)! Ahora sos nivel **{nuevo_lvl}**."
                    ),
                    inline=False
                )
            else:
                # El umbral debe coincidir con el de tu función de nivel
                exp_necesaria = int(150 * (nuevo_lvl ** 1.3))

                embed.add_field(
                    name="⭐ Experiencia",
                    value=(
                        f"Ganaste **{exp_total} XP**.\n"
                        f"Progreso: **{exp_restante}/{exp_necesaria} XP**"
                    ),
                    inline=False
                )

            # ---------- Collage ----------
            materiales = db.obtener_materiales()
            materiales_by_id = {m["id"]: m for m in materiales}

            rutas_imagenes = []
            for item_id in agrupados:
                item = materiales_by_id.get(item_id)
                if item and item["url"] and os.path.isfile(item["url"]):
                    rutas_imagenes.append(item["url"])

            collage_path = crear_collage(rutas_imagenes)
            files = []
            if collage_path:
                files.append(File(collage_path))
                embed.set_image(url=f"attachment://{os.path.basename(collage_path)}")
            # -----------------------------

            await interaction.response.send_message(embed=embed, files=files)

        except Exception as e:
            print(f"[FORAGE] ERROR: {e}")
            await interaction.response.send_message(
                "⚠️ Ocurrió un error durante la recolección.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ForageCommand(bot))