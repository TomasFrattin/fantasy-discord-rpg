
from datetime import datetime
from utils.db import conectar

def registrar_jugador(user_id, username, afinidad):
    energia_inicial = energia_max_por_afinidad(afinidad)

    conn = conectar()
    cursor = conn.cursor()
    now_iso = datetime.now().replace(microsecond=0).isoformat(sep=' ')
    cursor.execute("""
        INSERT OR IGNORE INTO jugadores 
        (user_id, username, afinidad, energia, energia_max, last_reset)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, afinidad, energia_inicial, energia_inicial, now_iso))
    conn.commit()
    conn.close()

def energia_max_por_afinidad(afinidad: str) -> int:
    base = 3
    if afinidad.lower() == "arcano":
        return base + 1
    return base

def resetear_jugador(user_id: str):
    conn = conectar()
    cursor = conn.cursor()

    # Traer datos del usuario
    cursor.execute("""
        SELECT vida, vida_max, afinidad
        FROM jugadores
        WHERE user_id = ?
    """, (user_id,))
    
    jugador = cursor.fetchone()

    # Si no existe, salir
    if not jugador:
        conn.close()
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

    conn.commit()
    conn.close()

    return True

def eliminar_jugador(user_id: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jugadores WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def resetear_todos():
    conn = conectar()
    cursor = conn.cursor()

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

        # Recuperar vida como ya tenías
        recuperar = max(1, int(vida_max * 0.20))
        nueva_vida = min(vida_actual + recuperar, vida_max)
        cursor.execute(
            "UPDATE jugadores SET vida = ? WHERE user_id = ?",
            (nueva_vida, user_id)
        )


    conn.commit()
    conn.close()

def sumar_oro(user_id, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET oro = oro + ? WHERE user_id = ?", (cantidad, user_id))
    conn.commit()
    conn.close()

def obtener_energia(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE user_id = ?", (user_id,))
    fila = cursor.fetchone()
    conn.close()
    return fila[0] if fila else None

def gastar_energia(user_id, cantidad=1):
    energia_actual = obtener_energia(user_id)
    if energia_actual is None:
        return None

    nueva = max(energia_actual - cantidad, 0)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET energia = ? WHERE user_id = ?", (nueva, user_id))
    conn.commit()
    conn.close()

    return nueva