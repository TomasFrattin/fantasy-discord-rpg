import json
import sqlite3
from config import DB_FILE, ENERGIA_MAX
from datetime import datetime
import random
from config import DB_FILE

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
    now_iso = datetime.now().replace(microsecond=0).isoformat(sep=' ')
    cursor.execute("""
        INSERT OR IGNORE INTO jugadores 
        (id_usuario, username, afinidad, energia, last_reset)
        VALUES (?, ?, ?, ?, ?)
    """, (id_usuario, username, afinidad, ENERGIA_MAX, now_iso))
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


def recolectar_materiales(user_id: str):
    conn = conectar()
    cursor = conn.cursor()

    # Traer todos los materiales de la DB
    cursor.execute("SELECT * FROM items WHERE tipo = 'material'")
    materiales = cursor.fetchall()

    if not materiales:
        conn.close()
        return []

    # Preparar pool con peso y cantidad máxima
    pool = {}
    for item in materiales:
        rareza = item["rareza"] or "comun"
        if rareza == "comun":
            peso, max_q = 50, 3
        elif rareza == "raro":
            peso, max_q = 20, 2
        elif rareza == "epico":
            peso, max_q = 5, 1
        else:
            peso, max_q = 1, 1
        pool[item["id"]] = {"peso": peso, "max_q": max_q, "nombre": item["nombre"]}

    # Elegir entre 1 y 5 materiales distintos
    n_types = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]

    # Selección ponderada sin repetición
    ids, pesos = zip(*[(k, v["peso"]) for k, v in pool.items()])
    chosen_ids = []
    while len(chosen_ids) < n_types and ids:
        selected = random.choices(ids, weights=pesos)[0]
        if selected not in chosen_ids:
            chosen_ids.append(selected)

    # Asignar cantidad aleatoria y agregar al inventario
    resultados = []
    for item_id in chosen_ids:
        max_q = pool[item_id]["max_q"]
        nombre = pool[item_id]["nombre"]
        cantidad = random.randint(1, max_q)
        agregar_item(user_id, item_id, cantidad)
        resultados.append((item_id, nombre, cantidad))

    conn.close()
    return resultados

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

    cursor.execute("SELECT id_usuario, vida, vida_max FROM jugadores")
    jugadores = cursor.fetchall()

    now_iso = datetime.now().replace(microsecond=0).isoformat(sep=' ')

    for jugador in jugadores:
        user_id = jugador["id_usuario"]
        vida_actual = jugador["vida"]
        vida_max = jugador["vida_max"]

        # Recuperar energía al máximo y actualizar last_reset
        cursor.execute(
            "UPDATE jugadores SET energia = ?, last_reset = ? WHERE id_usuario = ?",
            (ENERGIA_MAX, now_iso, user_id)
        )

        # Recuperar 10% de la vida máxima (igual que sleep)
        recuperar = max(1, int(vida_max * 0.10))
        nueva_vida = min(vida_actual + recuperar, vida_max)
        cursor.execute(
            "UPDATE jugadores SET vida = ? WHERE id_usuario = ?",
            (nueva_vida, user_id)
        )

    conn.commit()
    conn.close()

def eliminar_jugador(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jugadores WHERE id_usuario = ?", (user_id,))
    conn.commit()
    conn.close()


def obtener_materiales():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE tipo='material'")
    items = cursor.fetchall()
    conn.close()
    return items

def obtener_consumibles():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE tipo='consumible'")
    items = cursor.fetchall()
    conn.close()
    return items

def obtener_equipables():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE tipo IN ('arma','armadura','casco','botas')")
    items = cursor.fetchall()
    conn.close()
    return items


def actualizar_accion(id_usuario: str, accion: str | None):
    """Actualiza la acción actual del jugador (pescando, etc.)"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET accion_actual = ? WHERE id_usuario = ?", (accion, id_usuario))
    conn.commit()
    conn.close()

def obtener_accion_actual(id_usuario: str) -> str | None:
    """Obtiene la acción actual del jugador (pescando, etc.)"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT accion_actual FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()
    conn.close()
    return fila["accion_actual"] if fila else None

def actualizar_accion_fin(id_usuario: str, accion_fin: str | None):
    """Actualiza la fecha/hora de finalización de la acción actual del jugador."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jugadores SET accion_fin = ? WHERE id_usuario = ?",
        (accion_fin, id_usuario)
    )
    conn.commit()
    conn.close()

def obtener_accion_fin(id_usuario: str) -> str | None:
    """Obtiene la fecha/hora de finalización de la acción actual del jugador."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT accion_fin FROM jugadores WHERE id_usuario = ?",
        (id_usuario,)
    )
    fila = cursor.fetchone()
    conn.close()
    return fila["accion_fin"] if fila else None



def agregar_columna_accion_fin():
    """Agrega la columna 'accion_fin' a la tabla jugadores si no existe."""
    conn = conectar()
    cursor = conn.cursor()

    # Revisar columnas existentes
    cursor.execute("PRAGMA table_info(jugadores)")
    columnas = [col[1] for col in cursor.fetchall()]

    if "accion_fin" not in columnas:
        cursor.execute("ALTER TABLE jugadores ADD COLUMN accion_fin TEXT DEFAULT NULL")
        print("Columna 'accion_fin' agregada correctamente.")
    else:
        print("La columna 'accion_fin' ya existe.")

    conn.commit()
    conn.close()
