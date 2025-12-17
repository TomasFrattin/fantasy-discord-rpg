# commands/contribution.py
import discord
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
from services.jugadores import obtener_jugador, sumar_oro
from services.contribution import (
    crear_fondo,
    obtener_fondo,
    actualizar_fondo,
    registrar_contribucion,
    total_contribuido,
    fondo_alcanzado, barra_progreso
)
from services.contribution import FONDO_MERCHANT, OBJETIVO_MERCHANT, barra_progreso



class ContributionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Asegurarse de que el fondo existe al iniciar el bot
        crear_fondo(FONDO_MERCHANT, OBJETIVO_MERCHANT)

    @app_commands.command(
        name="contribuir",
        description="Contribuir oro para reparar el merchant y desbloquearlo"
    )
    @app_commands.describe(cantidad="Cantidad de oro que querés aportar")
    async def contribuir(self, interaction: Interaction, cantidad: int):
        user_id = str(interaction.user.id)
        jugador = obtener_jugador(user_id)

        fondo = obtener_fondo(FONDO_MERCHANT)
        if fondo_alcanzado(FONDO_MERCHANT):
            embed = Embed(
                title="🎉 Fondo completado",
                description=(
                    f"🏰 **Nunca has visto un mercado tan espléndido**. Las tiendas están cuidadosamente preparadas, "
                    f"las telas ondean con el viento y los estandartes brillan bajo el sol 🌞.\n\n"
                    f"Se escuchan las voces de los habitantes del reino, murmurando emocionados que los mercaderes "
                    f"no tardarán en llegar 🗣️✨.\n\n"
                    f"🎁 Carros llenos de mercancías, aromas de especias y pan recién horneado llegan a tu imaginación, "
                    f"mientras todo el mercado espera la llegada de los comerciantes.\n\n"
                    f"💰 **El fondo ya ha alcanzado su objetivo de {fondo['objetivo']} de oro** y pronto podrás disfrutar "
                    f"de las riquezas y maravillas que traerá el merchant."
                ),
                color=Color.green()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not jugador:
            return await interaction.response.send_message(
                "❌ No tenés un personaje creado todavía.",
                ephemeral=True
            )

        if jugador["oro"] < cantidad:
            return await interaction.response.send_message(
                f"❌ No tenés suficiente oro para aportar {cantidad}.",
                ephemeral=True
            )

        # Restar oro al jugador
        sumar_oro(user_id, -cantidad)

        # Actualizar pozo
        fondo = obtener_fondo(FONDO_MERCHANT)
        nuevo_acumulado = fondo["acumulado"] + cantidad
        actualizar_fondo(FONDO_MERCHANT, nuevo_acumulado)

        # Registrar contribución individual
        registrar_contribucion(user_id, FONDO_MERCHANT, cantidad)

        # Crear embed de feedback
        embed = Embed(color=Color.gold())
        embed.set_author(name=f"{jugador['username']} aportó {cantidad} de oro")

        if fondo_alcanzado(FONDO_MERCHANT):
            embed.title = "🎉 Fondo alcanzado"
            embed.description=(
                f"🏰 **Nunca has visto un mercado tan espléndido**. Las tiendas están cuidadosamente preparadas, "
                f"las telas ondean con el viento y los estandartes brillan bajo el sol 🌞.\n\n"
                f"Se escuchan las voces de los habitantes del reino, murmurando emocionados que los mercaderes "
                f"no tardarán en llegar 🗣️✨.\n\n"
                f"🎁 Carros llenos de mercancías, aromas de especias y pan recién horneado llegan a tu imaginación, "
                f"mientras todo el mercado espera la llegada de los comerciantes.\n\n"
                f"💰 **El fondo ya ha alcanzado su objetivo de {fondo['objetivo']} de oro** y pronto podrás disfrutar "
                f"de las riquezas y maravillas que traerá el merchant."
            )

            # Enviar embed principal del fondo alcanzado
            await interaction.response.send_message(embed=embed)

            # Mensaje informativo de recompensas
            await interaction.followup.send("🎁 ¡Las recompensas han sido entregadas automáticamente a los 3 mejores contribuyentes!")

            # Dar recompensas automáticamente al top 3
            from services.ranking import ranking_fondo_visual
            from services.rewards import recompensar_top

            top_ranking, _, _ = ranking_fondo_visual(FONDO_MERCHANT, top=3)
            await recompensar_top(interaction, top_ranking)

        else:
            restante = fondo["objetivo"] - nuevo_acumulado
            embed.title = "💰 Contribución exitosa"
            embed.description = (
                f"Aportaste {cantidad} de oro.\n"
                f"Faltan **{restante} de oro** para desbloquear **el merchant.**"
            )
            barra, porcentaje = barra_progreso(nuevo_acumulado, fondo['objetivo'])
            embed.add_field(
                name="Progreso del fondo",
                value=f"{barra} {porcentaje}%",
                inline=False
            )

            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ContributionCommand(bot))
