import sqlite3
from contextlib import contextmanager
from config import DB_FILE
import random


LLAVES_POR_DUNGEON = {
    1: "llave_cripta_antigua",
    2: "llave_abismo_coloso",
    3: "llave_santuario_eclipse",
    4: "llave_trono_vacio",
    5: "llave_trono_apocalipsis",
}


def obtener_llave_dungeon(dungeon_id):
    return LLAVES_POR_DUNGEON.get(int(dungeon_id))

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

def obtener_lista_dungeons():
    """
    Devuelve una lista de dungeons disponibles.
    Cada item es un dict con keys: 'id', 'nombre'
    """
    dungeons = []
    with get_cursor() as cursor:
        cursor.execute("SELECT id, nombre, nivel_recomendado FROM dungeon")
        rows = cursor.fetchall()
        for row in rows:
            dungeons.append({
                "id": row["id"],
                "nombre": row["nombre"],
                "nivel_recomendado": row["nivel_recomendado"]
            })
    return dungeons

def obtener_dungeon(dungeon_id):
    """
    Devuelve un diccionario con la dungeon y sus bosses.
    Los bosses tendrán siempre las keys: 'id', 'nombre', 'hp', 'atk'.
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM dungeon WHERE id = ?", (dungeon_id,))
        dungeon = cursor.fetchone()
        if not dungeon:
            return None

        # Traer bosses de la dungeon
        cursor.execute("SELECT * FROM boss WHERE dungeon_id = ?", (dungeon_id,))
        bosses_raw = cursor.fetchall()

        bosses = []
        for b in bosses_raw:
            bosses.append({
                "id": b["id"],
                "nombre": b["nombre"],
                "hp": b["vida"],       # columna original en DB
                "atk": b["damage"]     # columna original en DB
            })

        return {
            "id": dungeon["id"],
            "nombre": dungeon["nombre"],
            "oro_recompensa": dungeon["oro_recompensa"],
            "bosses": bosses
        }

def elegir_boss_aleatorio(dungeon):
    """Devuelve un boss aleatorio de la dungeon."""
    return random.choice(dungeon["bosses"])
