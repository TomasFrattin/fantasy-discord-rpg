def _barra(actual, maximo, segmentos=10):
    if maximo <= 0:
        return "░" * segmentos
    llenos = round((actual / maximo) * segmentos)
    llenos = max(0, min(llenos, segmentos))
    return "█" * llenos + "░" * (segmentos - llenos)


def formatear_estado_jugador(jugador):
    vida = jugador["vida"]
    vida_max = jugador["vida_max"]
    energia = jugador["energia"]
    energia_max = jugador["energia_max"]

    return (
        f"❤️ **Vida:** {vida} / {vida_max}\n"
        f"`{_barra(vida, vida_max)}`\n\n"
        f"⚡ **Energía:** {energia} / {energia_max}\n"
        f"`{_barra(energia, energia_max)}`\n\n"
        f"💰 **Oro:** {jugador['oro']}"
    )
