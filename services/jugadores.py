
from datetime import datetime
import sqlite3
from config import DB_FILE
from contextlib import contextmanager
from services.reglas import energia_max_por_afinidad

def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

@contextmanager
def get_cursor():
    conn = conectar()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()


def registrar_jugador(user_id, username, afinidad):
    energia_inicial = energia_max_por_afinidad(afinidad)
    now_iso = datetime.now().replace(microsecond=0).isoformat(sep=' ')

    with get_cursor() as cursor:
        cursor.execute("""
            INSERT OR IGNORE INTO jugadores 
            (user_id, username, afinidad, energia, energia_max, last_reset)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, afinidad, energia_inicial, energia_inicial, now_iso))


def obtener_jugador(user_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM jugadores WHERE user_id = ?", (user_id,))
        return cursor.fetchone()


def resetear_jugador(user_id: str):
    with get_cursor() as cursor:
        # Traer datos del usuario
        cursor.execute("""
            SELECT vida, vida_max, afinidad
            FROM jugadores
            WHERE user_id = ?
        """, (user_id,))
        jugador = cursor.fetchone()

        if not jugador:
            return False

        vida_actual = jugador["vida"]
        vida_max = jugador["vida_max"]
        afinidad = jugador["afinidad"]

        # Calcular energía máxima según afinidad
        energia_max = energia_max_por_afinidad(afinidad)

        # Resetear energía
        cursor.execute(
            "UPDATE jugadores SET energia = ? WHERE user_id = ?",
            (energia_max, user_id)
        )

        # Recuperar vida
        recuperar = max(1, int(vida_max * 0.10))
        nueva_vida = min(vida_actual + recuperar, vida_max)
        cursor.execute(
            "UPDATE jugadores SET vida = ? WHERE user_id = ?",
            (nueva_vida, user_id)
        )

    return True


def eliminar_jugador(user_id: str):
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM jugadores WHERE user_id = ?", (user_id,))


def resetear_todos():
    with get_cursor() as cursor:
        cursor.execute("SELECT user_id, vida, vida_max, afinidad FROM jugadores")
        jugadores = cursor.fetchall()

        for jugador in jugadores:
            user_id = jugador["user_id"]
            vida_actual = jugador["vida"]
            vida_max = jugador["vida_max"]
            afinidad = jugador["afinidad"]

            energia_max = energia_max_por_afinidad(afinidad)
            cursor.execute(
                "UPDATE jugadores SET energia = ? WHERE user_id = ?",
                (energia_max, user_id)
            )

            recuperar = max(1, int(vida_max * 0.20))
            nueva_vida = min(vida_actual + recuperar, vida_max)
            cursor.execute(
                "UPDATE jugadores SET vida = ? WHERE user_id = ?",
                (nueva_vida, user_id)
            )


def sumar_oro(user_id, cantidad):
    with get_cursor() as cursor:
        cursor.execute("UPDATE jugadores SET oro = oro + ? WHERE user_id = ?", (cantidad, user_id))


def obtener_energia(user_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT energia FROM jugadores WHERE user_id = ?", (user_id,))
        fila = cursor.fetchone()
        return fila[0] if fila else None


def gastar_energia(user_id, cantidad=1):
    energia_actual = obtener_energia(user_id)
    if energia_actual is None:
        return None

    nueva = max(energia_actual - cantidad, 0)

    with get_cursor() as cursor:
        cursor.execute("UPDATE jugadores SET energia = ? WHERE user_id = ?", (nueva, user_id))

    return nueva


def sleep(user_id: str):
    with get_cursor() as cursor:
        cursor.execute("SELECT vida, vida_max FROM jugadores WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        vida_actual, vida_max = row["vida"], row["vida_max"]

        recuperar = max(1, int(vida_max * 0.20))
        nueva_vida = min(vida_actual + recuperar, vida_max)

        cursor.execute("UPDATE jugadores SET vida = ? WHERE user_id = ?", (nueva_vida, user_id))

    return nueva_vida, recuperar


def actualizar_vida(user_id, nueva_vida):
    with get_cursor() as cursor:
        cursor.execute("UPDATE jugadores SET vida = ? WHERE user_id = ?", (nueva_vida, user_id))

def actualizar_cana(user_id, cana):
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE jugadores SET cana_equipada = ? WHERE user_id = ?",
            (cana, user_id)
        )
