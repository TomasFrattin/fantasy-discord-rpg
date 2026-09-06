import logging
import random
import time
import uuid
import discord

from config import EVENTOS_MODO_PRUEBA, WELCOME_CHANNELS
from utils import db
from data.texts import MAREA_ABISMOS_INICIO, MAREA_ABISMOS_FIN


EVENT_DEFINITIONS = {
    "marea_de_los_abismos": {
        "titulo": "🌊 La Marea de los Abismos",
        "duracion_horas": (2, 6),
        "intervalo_minimo_horas": 24,
        "recompensas": [
            {"item_id": "llave_cripta_antigua", "tier": 1, "probabilidades": {1: 0.001, 2: 0.004, 3: 0.008, 4: 0.012, 5: 0.008}},
            {"item_id": "llave_abismo_coloso", "tier": 2, "probabilidades": {1: 0, 2: 0.0005, 3: 0.002, 4: 0.005, 5: 0.008}},
            {"item_id": "llave_santuario_eclipse", "tier": 3, "probabilidades": {1: 0, 2: 0, 3: 0.0003, 4: 0.001, 5: 0.003}},
            {"item_id": "llave_trono_vacio", "tier": 4, "probabilidades": {1: 0, 2: 0, 3: 0, 4: 0.0002, 5: 0.001}},
            {"item_id": "llave_trono_apocalipsis", "tier": 5, "probabilidades": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0.0001}},
        ],
        "actividades": {"pesca": True},
    }
}


def evento_activo(event_id=None):
    return db.obtener_evento_activo(event_id)


def intentar_recompensa_evento(user_id, actividad, tier):
    """Hace una tirada especial para una actividad y registra el límite."""
    evento = evento_activo()
    if not evento:
        return None

    definicion = EVENT_DEFINITIONS[evento["event_id"]]
    if not definicion.get("actividades", {}).get(actividad):
        return None

    disponibles = []
    for recompensa in definicion["recompensas"]:
        if recompensa["tier"] > tier:
            continue
        if db.usuario_obtuvo_recompensa_evento(evento["instance_id"], user_id, recompensa["item_id"]):
            continue
        probabilidad = recompensa["probabilidades"].get(tier, 0)
        if probabilidad > 0:
            disponibles.append((recompensa, probabilidad))

    if EVENTOS_MODO_PRUEBA:
        if not disponibles:
            return None
        recompensa = random.choice(disponibles)[0]
    else:
        for recompensa, probabilidad in sorted(disponibles, key=lambda item: item[0]["tier"], reverse=True):
            if random.random() < probabilidad:
                break
        else:
            return None

    if not db.registrar_recompensa_evento(evento["instance_id"], user_id, recompensa["item_id"]):
        return None
    return db.obtener_item_por_id(recompensa["item_id"])


def intentar_recompensa_pesca(user_id, cana_tier):
    return intentar_recompensa_evento(user_id, "pesca", cana_tier)


def _duracion_y_intervalo(definicion):
    if EVENTOS_MODO_PRUEBA:
        return 5 * 60, 60
    minimo, maximo = definicion["duracion_horas"]
    return random.randint(minimo * 3600, maximo * 3600), definicion["intervalo_minimo_horas"] * 3600


async def procesar_eventos(bot):
    ahora = int(time.time())
    activo = db.obtener_evento_activo()
    if activo and activo["ends_at"] <= ahora:
        db.finalizar_evento(activo["instance_id"], ahora)
        await _anunciar(
            bot,
            "🌘 La Marea de los Abismos se retira",
            random.choice(MAREA_ABISMOS_FIN),
            0x34495E,
        )
        activo = None

    if activo:
        return

    for event_id, definicion in EVENT_DEFINITIONS.items():
        ultimo = db.obtener_ultimo_evento(event_id)
        if ultimo and ahora < ultimo["ends_at"] + _duracion_y_intervalo(definicion)[1]:
            continue
        duracion, _ = _duracion_y_intervalo(definicion)
        instancia = f"{event_id}_{uuid.uuid4().hex[:10]}"
        db.crear_evento(instancia, event_id, ahora, ahora + duracion)
        await _anunciar(
            bot,
            definicion["titulo"],
            random.choice(MAREA_ABISMOS_INICIO),
            0x1ABC9C,
        )
        logging.info("[EVENT] Inició %s (%s segundos)", event_id, duracion)
        break


async def _anunciar(bot, titulo, descripcion, color):
    embed = discord.Embed(title=titulo, description=descripcion, color=color)
    for channel_id in WELCOME_CHANNELS:
        canal = bot.get_channel(channel_id)
        if canal:
            try:
                await canal.send(embed=embed)
            except Exception:
                logging.exception("No se pudo anunciar un evento en el canal %s", channel_id)
