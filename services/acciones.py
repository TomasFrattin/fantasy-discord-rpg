
from utils.db import get_cursor

def actualizar_accion(user_id: str, accion: str | None):
    with get_cursor() as cursor:
        cursor.execute("UPDATE jugadores SET accion_actual = ? WHERE user_id = ?", (accion, user_id))

def obtener_accion_actual(user_id: str) -> str | None:
    with get_cursor() as cursor:
        cursor.execute("SELECT accion_actual FROM jugadores WHERE user_id = ?", (user_id,))
        fila = cursor.fetchone()
        return fila["accion_actual"] if fila else None

def actualizar_accion_fin(user_id: str, accion_fin: str | None):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE jugadores SET accion_fin = ? WHERE user_id = ?",
            (accion_fin, user_id)
        )

def obtener_accion_fin(user_id: str) -> str | None:
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT accion_fin FROM jugadores WHERE user_id = ?",
            (user_id,)
        )
        fila = cursor.fetchone()
        return fila["accion_fin"] if fila else None

