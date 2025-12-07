from discord import File, app_commands, Interaction, Embed
from discord.ext import commands
from utils import db
from data.texts import RECOLECTAR_DESCRIPTIONS
import random
import os
from PIL import Image
from utils.messages import mensaje_usuario_no_creado, mensaje_sin_energia

def crear_collage(rutas, tamaño_celda=(128, 128), gap=10):
    if not rutas:
        return None

    cols = min(3, len(rutas))
    filas = (len(rutas) + cols - 1) // cols
    ancho = cols * tamaño_celda[0] + (cols - 1) * gap
    alto = filas * tamaño_celda[1] + (filas - 1) * gap
    collage = Image.new("RGBA", (ancho, alto), (255, 255, 255, 0))

    for idx, ruta in enumerate(rutas):
        img = Image.open(ruta).convert("RGBA").resize(tamaño_celda)
        x = (idx % cols) * (tamaño_celda[0] + gap)
        y = (idx // cols) * (tamaño_celda[1] + gap)
        collage.paste(img, (x, y), img)

    output_path = "data/temp/temp_collage.png"
    collage.save(output_path)
    return output_path

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

        db.gastar_energia(user_id, 1)

        try:
            resultados = db.recolectar_materiales(user_id)
            if not resultados:
                return await interaction.response.send_message("No conseguiste ningún material esta vez.", ephemeral=True)

            texto_flavor = random.choice(RECOLECTAR_DESCRIPTIONS)

            # Agrupar duplicados
            agrupados = {}
            for item_id, nombre, cantidad in resultados:
                if item_id not in agrupados:
                    agrupados[item_id] = {"nombre": nombre, "cantidad": 0}
                agrupados[item_id]["cantidad"] += cantidad

            embed = Embed(
                title="🧺 Recolección completada",
                description=texto_flavor,
                color=0x00ff00
            )

            for item_id, info in agrupados.items():
                embed.add_field(
                    name=info["nombre"],
                    value=f"Cantidad: × {info['cantidad']}",
                    inline=True
                )

            # Obtener todos los materiales desde DB solo una vez
            materiales = db.obtener_materiales()
            materiales_by_id = {m["id"]: m for m in materiales}

            # Crear collage solo para items que tengan URL en DB
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

            await interaction.response.send_message(embed=embed, files=files)

        except Exception as e:
            print(f"[FORAGE] ERROR: {e}")
            await interaction.response.send_message(
                "⚠️ Ocurrió un error durante la recolección.", ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ForageCommand(bot))
