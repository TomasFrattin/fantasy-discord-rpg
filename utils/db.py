import json
import sqlite3
from config import DB_FILE, ENERGIA_MAX
from datetime import datetime
import random
from data.texts import RECOLECTAR_DESCRIPTIONS
from data_loader import MATERIALES

# -------------------- CONEXIÓN --------------------
def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

# -------------------- STATS --------------------
def recalcular_stats(id_usuario):
    """Recalcula daño y vida en base al equipamiento."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vida_base, base_damage, 
               arma_equipada, armadura_equipada, casco_equipado, botas_equipadas
        FROM jugadores WHERE id_usuario = ?
    """, (id_usuario,))
    pj = cursor.fetchone()

    if not pj:
        conn.close()
        return

    base_hp = pj["vida_base"]
    base_dmg = pj["base_damage"]

    bonus_hp = 0
    bonus_dmg = 0

    from data_loader import EQUIPABLES_BY_ID  # evita import circular

    # ARMA
    if pj["arma_equipada"]:
        arma = EQUIPABLES_BY_ID.get(pj["arma_equipada"])
        if arma:
            bonus_dmg += arma["stats"].get("ataque", 0)

    # ARMADURA / CASCO / BOTAS
    for slot in ("armadura_equipada", "casco_equipado", "botas_equipadas"):
        if pj[slot]:
            item = EQUIPABLES_BY_ID.get(pj[slot])
            if item:
                bonus_hp += item["stats"].get("vida", 0)

    # actualizar stats finales
    cursor.execute("""
        UPDATE jugadores
        SET vida_max = ?, damage = ?, vida = MIN(vida, ?)
        WHERE id_usuario = ?
    """, (base_hp + bonus_hp, base_dmg + bonus_dmg, base_hp + bonus_hp, id_usuario))

    conn.commit()
    conn.close()


def sleep(user_id: str):
    conn = conectar()
    cursor = conn.cursor()

    # Obtener vida actual y vida máxima real
    cursor.execute("SELECT vida, vida_max FROM jugadores WHERE id_usuario = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    vida_actual, vida_max = row["vida"], row["vida_max"]

    # Recupera el 10% de la vida máxima (mínimo 1)
    recuperar = max(1, int(vida_max * 0.10))
    nueva_vida = min(vida_actual + recuperar, vida_max)

    cursor.execute(
        "UPDATE jugadores SET vida = ? WHERE id_usuario = ?",
        (nueva_vida, user_id)
    )

    conn.commit()
    conn.close()

    return nueva_vida, recuperar


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

def actualizar_vida(user_id, nueva_vida):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET vida = ? WHERE id_usuario = ?", (nueva_vida, user_id))
    conn.commit()
    conn.close()
# -------------------- INVENTARIO --------------------
# REFACTORIZAR
# def agregar_consumible(id_usuario, item_id):
#     conn = conectar()
#     cursor = conn.cursor()

#     cursor.execute("SELECT inventario FROM jugadores WHERE id_usuario = ?", (id_usuario,))
#     fila = cursor.fetchone()

#     inv = json.loads(fila[0]) if fila else []
#     inv.append(item_id)

#     cursor.execute("UPDATE jugadores SET inventario = ? WHERE id_usuario = ?", (json.dumps(inv), id_usuario))
#     conn.commit()
#     conn.close()

# --- inventario / items helpers ---

def agregar_item(user_id: str, item_id: str, cantidad: int = 1):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inventario (user_id, item_id, cantidad) VALUES (?, ?, ?)"
        " ON CONFLICT(user_id, item_id) DO UPDATE SET cantidad = cantidad + ?",
        (user_id, item_id, cantidad, cantidad)
    )
    conn.commit()
    conn.close()

def obtener_inventario(user_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.item_id, it.nombre, i.cantidad, it.tipo, it.rareza
        FROM inventario i
        JOIN items it ON it.id = i.item_id
        WHERE i.user_id = ?
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"item_id": r[0], "nombre": r[1], "cantidad": r[2], "tipo": r[3], "rareza": r[4]} for r in rows]

import random

from data_loader import MATERIALES

def recolectar_materiales(user_id: str):
    """Lógica de recolección: selecciona items y devuelve resultados."""
    import random
    pool = []
    for item in MATERIALES:
        rareza = item.get("rareza", "comun")
        if rareza == "comun":
            max_q, peso = 3, 50
        elif rareza == "raro":
            max_q, peso = 2, 20
        else:
            max_q, peso = 1, 5
        pool.append((item["id"], peso, max_q))

    n_types = random.choices([1, 2, 3], weights=[60,30,10])[0]
    chosen = random.choices(pool, weights=[p[1] for p in pool], k=n_types)

    resultados = []
    for item_id, _, max_q in chosen:
        cantidad = random.randint(1, max_q)
        agregar_item(user_id, item_id, cantidad)
        resultados.append((item_id, cantidad))

    mapping = {item["id"]: item["nombre"] for item in MATERIALES}
    return [(item_id, mapping.get(item_id, item_id), cantidad) for item_id, cantidad in resultados]

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
