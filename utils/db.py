import json
import sqlite3
from config import DB_FILE, ENERGIA_MAX
from datetime import datetime

def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def borrar_tabla_jugadores():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS jugadores")
    conn.commit()
    conn.close()

def crear_tabla_jugadores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS jugadores (
        id_usuario TEXT PRIMARY KEY,
        username TEXT,
        afinidad TEXT,
        
        -- stats base
        base_vida INTEGER DEFAULT 100,
        base_damage INTEGER DEFAULT 10,

        -- stats finales
        vida INTEGER DEFAULT 100,
        damage INTEGER DEFAULT 10,

        energia INTEGER DEFAULT 30,

        exploracion INTEGER DEFAULT 0,
        combate INTEGER DEFAULT 0,
        caceria INTEGER DEFAULT 0,

        inventario TEXT DEFAULT '[]', 

        arma_equipada TEXT,
        armadura_equipada TEXT,
        casco_equipado TEXT,
        botas_equipadas TEXT,

        oro INTEGER DEFAULT 0,
        last_reset TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


# -------------------- STATS --------------------
def recalcular_stats(id_usuario):
    """Recalcula daño y vida en base al equipamiento."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT base_vida, base_damage, 
               arma_equipada, armadura_equipada, casco_equipado, botas_equipadas
        FROM jugadores WHERE id_usuario = ?
    """, (id_usuario,))
    pj = cursor.fetchone()

    if not pj:
        conn.close()
        return

    base_hp = pj["base_vida"]
    base_dmg = pj["base_damage"]

    bonus_hp = 0
    bonus_dmg = 0

    from data_loader import ITEMS_BY_ID  # evita import circular

    # ARMA
    if pj["arma_equipada"]:
        arma = ITEMS_BY_ID.get(pj["arma_equipada"])
        if arma:
            bonus_dmg += arma["stats"].get("ataque", 0)

    # ARMADURA / CASCO / BOTAS
    for slot in ("armadura_equipada", "casco_equipado", "botas_equipadas"):
        if pj[slot]:
            item = ITEMS_BY_ID.get(pj[slot])
            if item:
                bonus_hp += item["stats"].get("vida", 0)

    # actualizar stats finales
    cursor.execute("""
        UPDATE jugadores
        SET vida = ?, damage = ?
        WHERE id_usuario = ?
    """, (base_hp + bonus_hp, base_dmg + bonus_dmg, id_usuario))

    conn.commit()
    conn.close()


# -------------------- JUGADOR --------------------
def registrar_jugador(id_usuario, username, afinidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO jugadores 
        (id_usuario, username, afinidad, energia, last_reset)
        VALUES (?, ?, ?, ?, ?)
    """, (id_usuario, username, afinidad, ENERGIA_MAX, datetime.now()))
    conn.commit()
    conn.close()


def obtener_jugador(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    row = cursor.fetchone()
    conn.close()
    return row


# -------------------- INVENTARIO --------------------
def agregar_consumible(id_usuario, item_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT inventario FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()

    inv = json.loads(fila[0]) if fila else []
    inv.append(item_id)

    cursor.execute("UPDATE jugadores SET inventario = ? WHERE id_usuario = ?", (json.dumps(inv), id_usuario))
    conn.commit()
    conn.close()


# -------------------- EQUIPAMIENTO --------------------
def equipar(id_usuario, slot, item_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"UPDATE jugadores SET {slot} = ? WHERE id_usuario = ?", (item_id, id_usuario))
    conn.commit()
    conn.close()

    recalcular_stats(id_usuario)


# -------------------- ORO / ENERGÍA --------------------
def sumar_oro(id_usuario, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET oro = oro + ? WHERE id_usuario = ?", (cantidad, id_usuario))
    conn.commit()
    conn.close()


def obtener_energia(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()
    conn.close()
    return fila[0] if fila else None


def gastar_energia(id_usuario, cantidad=1):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()

    if fila:
        nueva = max(fila[0] - cantidad, 0)
        cursor.execute("UPDATE jugadores SET energia = ? WHERE id_usuario = ?", (nueva, id_usuario))
        conn.commit()

    conn.close()


def resetear_todos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jugadores
        SET energia = ?, last_reset = ?
    """, (ENERGIA_MAX, datetime.now()))
    conn.commit()
    conn.close()
