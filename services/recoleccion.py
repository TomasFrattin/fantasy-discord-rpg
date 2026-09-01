"""Reglas de negocio para la recolección de materiales."""

import random

from services.jugadores import obtener_jugador
from utils import db


def tiers_por_nivel(nivel_recoleccion: int) -> list[str]:
    if nivel_recoleccion < 5:
        return ["comun"]
    if nivel_recoleccion < 10:
        return ["comun", "raro"]
    if nivel_recoleccion < 15:
        return ["comun", "raro", "epico"]
    return ["comun", "raro", "epico", "legendario"]


def recolectar_materiales(user_id: str) -> list[tuple[str, str, int]]:
    """Elige materiales según el nivel del jugador y los agrega al inventario."""
    jugador = obtener_jugador(user_id)
    if not jugador:
        return []

    nivel = jugador["lvl_recoleccion"] or 1
    materiales = db.obtener_materiales()
    permitidas = tiers_por_nivel(nivel)
    pool = []

    for item in materiales:
        rareza = item["rareza"] or "comun"
        if rareza not in permitidas:
            continue

        peso, cantidad_maxima = {
            "comun": (50, 3),
            "raro": (20, 1),
            "epico": (5, 1),
            "legendario": (1, 1),
        }.get(rareza, (50, 1))
        pool.append((item["id"], item["nombre"], peso, cantidad_maxima))

    if not pool:
        return []

    tipos_a_obtener = random.randint(1, 2) if nivel < 5 else random.randint(2, 3) if nivel < 10 else random.randint(2, 4)
    tipos_a_obtener = min(tipos_a_obtener, len(pool))
    disponibles = pool[:]
    resultados = []

    for _ in range(tipos_a_obtener):
        elegido = random.choices(disponibles, weights=[item[2] for item in disponibles], k=1)[0]
        disponibles.remove(elegido)
        item_id, nombre, _, cantidad_maxima = elegido
        cantidad = random.randint(1, cantidad_maxima)
        db.agregar_item(user_id, item_id, cantidad)
        resultados.append((item_id, nombre, cantidad))

    return resultados


def agregar_experiencia(user_id: str, experiencia: int) -> tuple[int, int, int]:
    """Aplica experiencia de recolección y devuelve nivel, EXP restante y niveles subidos."""
    jugador = obtener_jugador(user_id)
    if not jugador:
        raise ValueError("Jugador no encontrado")

    exp_actual = (jugador["exp_recoleccion"] or 0) + experiencia
    nivel = jugador["lvl_recoleccion"] or 1
    niveles_subidos = 0

    while exp_actual >= int(150 * (nivel ** 1.3)):
        exp_actual -= int(150 * (nivel ** 1.3))
        nivel += 1
        niveles_subidos += 1

    db.actualizar_exp_recoleccion(user_id, exp_actual)
    db.actualizar_lvl_recoleccion(user_id, nivel)
    return nivel, exp_actual, niveles_subidos
