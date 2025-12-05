from discord import app_commands, Interaction
from discord.ext import commands
from utils import db

class SleepCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sleep", description="Recuperar 10% de tu vida máxima.")
    async def sleep(self, interaction: Interaction):
        print("Comando /sleep ejecutado")
        user_id = str(interaction.user.id)
        energia = db.obtener_energia(user_id)
        print(f"Energía: {energia}")

        row = db.obtener_jugador(user_id)
        print(f"Row: {row}")
        if not row:
            print("No tiene personaje")
            return await interaction.response.send_message(
                "⚠️ No tenés personaje. Usá **/start**.", ephemeral=True
            )

        if energia <= 0:
            print("No tiene energía")
            return await interaction.response.send_message(
                "⚠️ No te queda energía.",
                ephemeral=True
            )
        
        db.gastar_energia(user_id, 1)
        print("Gastó energía")

        nueva_vida, recuperado = db.sleep(user_id)
        print(f"Recuperado: {recuperado}, Nueva vida: {nueva_vida}")

        await interaction.response.send_message(
            f"😴 Descansás y recuperás **{recuperado}** de vida.\n"
            f"❤️ Vida actual: **{nueva_vida}**.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SleepCommand(bot))
