# services/ranking.py
from utils.db import get_cursor
from services.contribution import total_contribuido, obtener_fondo

def ranking_fondo_visual(fondo_id: str, top: int = 10) -> list[dict]:
    """
    Devuelve una lista de jugadores con su contribución y porcentaje sobre el total del fondo.
    """
    fondo = obtener_fondo(fondo_id)
    if not fondo:
        return []

    total_fondo = fondo["objetivo"]
    total_actual = total_contribuido(fondo_id)

    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT c.user_id, j.username, c.cantidad
            FROM contribuciones c
            JOIN jugadores j ON c.user_id = j.user_id
            WHERE c.fondo_id = ?
            ORDER BY c.cantidad DESC
            LIMIT ?
            """,
            (fondo_id, top)
        )
        resultados = []
        for fila in cursor.fetchall():
            jugador = dict(fila)
            jugador["porcentaje_objetivo"] = min(int((jugador["cantidad"] / total_fondo) * 100), 100)
            jugador["porcentaje_fondo_actual"] = min(int((jugador["cantidad"] / total_actual) * 100), 100) if total_actual else 0
            resultados.append(jugador)
        return resultados, total_actual, total_fondo
